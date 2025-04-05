<p align="center">
  <img src="https://github.com/1rvinn/mindpalace/blob/main/icon.jpg?raw=true" alt="Logo"/>
</p>

> [!TIP]
> try it out [here!](https://mindpalace.streamlit.app)


lately, i have been finding it really hard to go through excruciatingly long github repos and make sense of them (thanks to my reels afflicted short attention span :)). \
so, i built mindpalace - a tool that allows you to to parse through github repos effectively by generating file-wise explanations, and workflow breakdowns while also generating mind maps for you to learn visually. and the rag based ask ai feature, that allows you to ask anything and everything about the repo, serves as a cherry on top. i have also extended the functionality to pdf documents. \
works on any device, no api keys reqd, no downloads reqd.

https://github.com/user-attachments/assets/6a967d11-808e-473f-b4f5-30824b2c4e93

want to run it locally? here are the steps:
-------
1. ensure that python, pip and git are installed

        sudo apt update && sudo apt-get install python3
        sudo apt-get install python3-pip
        sudo apt install git
4. clone the github repo & cd into it

        git clone https://github.com/1rvinn/mindpalace.git && cd mindpalace
5. install the required libraries by creating a virtual environment

		python3 -m venv .venv
		source .venv/bin/activate
       pip install -r requirements.txt
7. get your api keys from gemini, mistral and github access tokem. then update them in .streamlit/secrets.toml as shown below

       ACCESS_TOKEN='add your access token here'
       MISTRAL_API_KEY='add your api key here'
        GEMINI_API_KEY='add your api key here'


9. run the app

        python3 -m streamlit run app.py

### pipeline
![pipeline](https://github.com/1rvinn/mindpalace/blob/main/pipeline_mp.png?raw=true)
