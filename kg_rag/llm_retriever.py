import os

import litellm
from ecologits import EcoLogits
from py2neo import Graph


class LLMRetriever:
    """KG retriever based on LLM for the RAG task."""

    def __init__(self) -> None:
        self.model_name = os.environ.get("GENERATION_MODEL")
        self.graph = Graph(
            uri=os.environ.get("GRAPH_URI"),
            user=os.environ.get("GRAPH_USER"),
            password=os.environ.get("GRAPH_PASSWORD"),
            name=os.environ.get("GRAPH_DATABASE"),
        )

    def _get_kg_schema(self) -> str:
        """Extract KG schema from Neo4j."""
        kg_schema = """Labels des noeuds et propriétés :
        Le type de noeud PieceIdentite a pour propriétés nom, infos
        PieceIdentite.nom peut prendre pour valeurs \"Passeport\" ou \"Carte d'identité\"}
        Le type de noeud Demande a pour propriétés nom, personne, lieu, infos
        Pour une carte d'identité, Demande.nom peut prendre pour valeurs \"Première demande\", \"Renouvellement\", \"Carte perdue\", \"Carte volée\"
        Pour un passeport, Demande.nom peut prendre pour valeurs \"Première demande\", \"Renouvellement\", \"Passeport perdu\", \"Passeport volé\", \"Passeport en urgence\"
        Demande.personne peut prendre pour valeurs \"majeure\" ou \"mineure\"
        Demande.lieu peut prendre pour valeurs \"en France\" ou \"à l'étranger\"
        Le type de noeud Etape a pour propriétés nom, numero, infos
        Le type de noeud Information a pour propriétés nom, infos
        
        Relations :
        (e:Etape)-[:CONCERNE]->(d:Demande)
        (i:Information)-[CONCERNE]->(d:Demande)
        (d:Demande)-[CONCERNE]->PieceIdentite"""
        return kg_schema

    def _generate_prompt(self, question: str) -> list[dict[str, str]]:
        """Generate contextualised prompt for query generation."""
        prompt = [
            {
                "role": "system",
                "content": """Tu es un assistant qui aide à formuler des requêtes Cypher.""",
            },
            {
                "role": "user",
                "content": """Ecrit une requête Cypher pour répondre à la question de l'utilisateur en te basant sur le schéma du graphe Neo4j donné.  
                Utilise uniquement les labels, les propriétés et les types de relation fournis dans le schéma.
                Respecte le sens des relations fournies indiqué par ->.
                N'ajoute aucun texte, tu dois uniquement répondre avec la requête Cypher générée.
                N'ajoute pas de majuscules aux entités extraites de la question.""",
            },
            {
                "role": "user",
                "content": f"""Schéma du graphe : {self._get_kg_schema()}""",
            },
            {
                "role": "user",
                "content": """Voici quelques exemples : 
                Question : J'ai 17 ans et je voudrais demander ma première carte d'identité, aide moi !
                MATCH (n)-[:CONCERNE]->(d:Demande {nom:"Première demande", personne:"mineure"})-[:CONCERNE]->(p:PieceIdentite {nom:"Carte d'identité"})
                RETURN n

                Question : Comment refaire ma carte d'identité si je suis une personne majeure résidant en France ?
                MATCH (n)-[:CONCERNE]->(d:Demande {nom:"Renouvellement", personne:"majeure", lieu:"en France"})-[:CONCERNE]->(p:PieceIdentite {nom:"Carte d'identité"})
                RETURN n
                
                Question : Quelles sont les informations à connaître pour refaire son passeport en urgence à l'étranger ?
                MATCH (i:Information)-[:CONCERNE]->(d:Demande {nom:"Passeport en urgence", lieu:"à l'étranger"})-[:CONCERNE]->(p:PieceIdentite {nom:"Passeport"})
                RETURN i
                
                Question : Ma fille mineure s'est faite volée son passeport à Paris, qu'est ce qu'on doit faire ?
                MATCH (n)-[:CONCERNE]->(d:Demande {nom:"Passeport volé, personne:"mineure", lieu:"en France"})-[:CONCERNE]->(p:PieceIdentite{nom:"Passeport"})""",
            },
            {
                "role": "user",
                "content": f"""Question : {question.lower()}""",
            },
        ]
        return prompt

    def _generate_query(self, prompt: list[dict[str, str]]) -> dict[str, any]:
        """Generate query with a LLM based on a given question and a graph schema."""
        EcoLogits.init(providers="litellm", electricity_mix_zone="SWE")
        response = litellm.completion(
            model=self.model_name, messages=prompt, temperature=0.0
        )
        output = {
            "query": response["choices"][0]["message"]["content"],
            "env_impacts": response.impacts,
        }
        return output

    def _execute_query(self, query: str) -> list[dict[str, any]]:
        """Execute query on the graph."""
        facts = self.graph.run(query).data()
        return facts

    def _format_facts(self, facts: list[dict[str, any]]) -> str:
        """Convert facts from Neo4j to text for the prompt content."""
        context = ""
        if len(facts) == 0:
            context = "[]"
        else:
            for fact in facts:
                context += f"{str(fact)} \n"
        return context

    def run(self, question: str) -> dict[str, any]:
        """Retrieve context for a question based on a graph.."""
        prompt = self._generate_prompt(question)
        query_output = self._generate_query(prompt)
        graph_context = self._execute_query(query_output["query"])
        output = {
            "query": query_output["query"],
            "context": self._format_facts(graph_context),
            "env_impacts": query_output["env_impacts"],
        }
        return output
