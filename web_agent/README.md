# Running a Web Agent on an Open-ended task

# Setup

Clone browsergym repository:
```sh
git clone https://github.com/ServiceNow/BrowserGym.git
```

Install dependencies:
```sh
cd browsergym/demo_agent/
pip install -r requirements.txt
```

Set your OpenAI API key:
```
export OPENAI_API_KEY=<YOUR_API_KEY>
```

Run the demo:
```sh
python run_demo.py --model_name <MODEL_TO_USE> --start_url <URL_OF_YOUR_WESBITE>
```
