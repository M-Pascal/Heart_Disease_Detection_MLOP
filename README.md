# Machine Learning Pipeline Summative (MLOP).

# Heart Disease Diagnosis Project

## Project overview
This project aims to develop a machine learning model to predict the likelihood of heart disease, a leading global cause of disability and death. Heart disease encompasses various conditions affecting the heart and circulatory system, often leading to severe complications like heart attacks and organ damage.
Early detection of heart disease can save lives by enabling timely intervention. A predictive model helps identify high-risk individuals, supports medical decision-making, and improves preventive care—reducing healthcare costs and improving patient outcomes.

## Dataset
### Key features:
- Heart disease Likelihood : Predicting whether you person is more likely to have heart related disease or not.
- Model Training: Enables users to train or retrain models using custom datasets.
- Interactive Visualizations: Displays model performance metrics such as accuracy, and confusion matrices.
- FastAPI: Provides endpoint-based interaction for seamless integration with external services.
- Scalable Deployment: Dockerized infrastructure for cloud deployment, tested locally.

## Project Structure
The project directories are structure in this manner;
```bash
Heart_Disease_Detection_MLOP/
│
├── README.md
│
├── notebook/
│   ├──Heart_Disease_MLOP.ipynb
│
├── src/
│   ├── static   # for styling, and js
│   ├── templates  # for html web pages
│   ├── api.py
│   ├── app.py
│   ├── preprocessing.py  # model preprocessing
│   ├── model.py   # for model training
│   └── prediction.py
│
├── data/
│   ├──train.csv
│   └── test.csv
│
└── models/
   ├── label_encoders.pkl
   └── logistic_regression.tf
```
## Project key Findings:

## Project Installation
1. Clone the repository:
``` bash
git clone https://github.com/M-Pascal/Heart_Disease_Detection_MLOP.git
```
2. Create Virtual environment and activate it (for Window users):
``` bash
python -m venv myenv
source venv/Script/activate
```
3. Install the dependencies on virtual environment using:
``` bash
pip install -r requirements.txt
```
## How to run the project
1. Start the FastAPI server:
``` bash
uvicorn src.api:app --reload 
```
Access it via this link: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
2. Start the Flask Web-App using a new terminal (open new terminal):
```bash
python -m flask --app .\app.py run
```
Access web-page via this link: [http://127.0.0.1:5000](http://127.0.0.1:5000)
## Demo-Video
[![Watch the video](https://img.youtube.com/vi/5aYpkLfkgRE/maxresdefault.jpg)](https://youtu.be/5aYpkLfkgRE)

### [Demo video_Template](https://youtu.be/5aYpkLfkgRE)

### Author
> Done by Pascal Mugisha