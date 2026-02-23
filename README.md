<a name="readme-top"></a>

# The Snowbasin "Congestion Engine"

## The Wildcats

- Dani Lopez (Data Analyst)
- Hazem Dawahi (Frontend and Backend Integration)
- Roberto Camposeco (Data Engineer)
- Kevin Bell (Data Miner)

## Project goal

Predict peak-hour traffic volume on Trappers Loop (SR-167) to optimize mountain resort staffing and parking operations 72 hours in advance.

## Sprint 3 modeling workflow

Run the full modeling and evaluation pipeline after generating processed data:

```bash
python src/data_cleaning.py
python src/train_model.py
```

Artifacts produced by `src/train_model.py`:

- `models/champion_model.joblib`
- `results/model_metrics.csv` (baseline vs. champion metrics)
- `results/training_summary.json`
- `results/actual_vs_predicted.svg`
- `results/residual_plot.svg`

## How to Run the App

Launch the Sprint 4 MVP dashboard locally with Gradio:

```bash
python src/train_model.py
python src/app.py
```

Open the URL displayed by Gradio (typically `http://localhost:7860`) and use the controls to generate real-time traffic predictions from the saved champion model.

### Data audit artifact

A full inventory of every CSV and Excel source currently in the repository is documented at:

- `docs/data_inventory.md`

## Links

- Dashboard: https://dashboard-snowbasin-wildcats.vercel.app/
- Data export endpoint: https://d34agsj343lfgw.cloudfront.net/

<!--
https://docs.google.com/spreadsheets/d/19SCDgp7Sh4boJbSSh4ONVqS9Zff8TVXjXxcgmYpLlhA/edit?gid=1263462889#gid=1263462889

https://drive.google.com/drive/folders/1ZYy-WkICLOp1482vwEbTc5UvLItbWs4y

https://udot.iteris-pems.com/#41.203198,-111.878929,12

https://prod-ut.ibi511.com/developers/doc

https://mesowest.utah.edu/cgi-bin/droman/variable_download_select.cgi
-->

<p align="right"><a href="#readme-top">back to top</a></p>
