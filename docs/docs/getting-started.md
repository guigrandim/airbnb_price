# Início rápido

## Aplicação Streamlit

Requisitos validados: Python 3.13.17 e dependências fixadas em `requirements.txt`.

No PowerShell, na raiz do repositório:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

O app carrega o pipeline salvo em `models/airbnb_amsterdam_price_v2.pkl`. Ele aceita os dados do anúncio, calcula as 36 features aprovadas pelo módulo `src/modeling/inference.py`, mostra a referência de preço e a faixa empírica, e permite comparar com o preço informado. A comparação financeira é apenas um cenário bruto para o anfitrião.

O modelo usa o snapshot de 06/12/2018. A saída é retrospectiva e não deve ser interpretada como recomendação de preço atual, preço ótimo, receita garantida ou ROI realizado.

## Notebook e dados

Use a mesma `.venv` para abrir `notebooks/price_prediction.ipynb` no JupyterLab. Os dados brutos ficam em `data/raw`; o teste permanece em `data/processed/df_test_raw.csv` sem limpeza até a avaliação final.

Para abrir o notebook depois de instalar as dependências:

```powershell
jupyter lab
```

O ambiente também contém o kernel e as extensões MCP de edição e execução incremental do notebook.
