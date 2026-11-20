# 🏘️ Airbnb Amsterdam — Estimativa de Preços por Diária com Machine Learning

Criei um simulador para ajudar quem procura hospedagem em Amsterdam a comparar o preço de uma diária com o valor estimado para aquele imóvel.

Você informa o bairro, as características da acomodação e a diária anunciada. O resultado mostra a referência calculada pelo modelo e a diferença em euros por noite. Um gráfico coloca os dois preços lado a lado.

Usei Streamlit na aplicação e LightGBM na previsão. Os dados são de dezembro de 2018, portanto a consulta demonstra a comparação de preços daquela base histórica.

![Python](https://img.shields.io/badge/Python-3.11–3.13-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.67-FF4B4B?logo=streamlit&logoColor=white)
![LightGBM](https://img.shields.io/badge/Modelo-LightGBM-29804A)
![Licença](https://img.shields.io/badge/licença-MIT-green)

🔗 **Aplicativo em produção:** [airbnbprice.streamlit.app](https://airbnbprice.streamlit.app/)

<p align="center">
<img src="./assets/amsterdam-night.png" alt="Ilustração fotográfica de Amsterdam ao anoitecer, gerada com IA para o cabeçalho do simulador" width="800">
</p>

### 🎯 Destaques

- O simulador mostra se a diária está abaixo, perto ou acima da referência. A localização é preenchida automaticamente pela escolha do bairro.
- O LightGBM final usa 36 variáveis e perda absoluta sem pesos. Em validação cruzada com 17.021 anúncios, obteve **23,30% de MAPE** e **€ 37,57 de MAE**.
- Na análise econômica de 20.026 anúncios, substituir os preços anunciados pelas referências resultou em **+€ 2,05 milhões (+1,75%) de volume bruto anual projetado**, mantendo as mesmas noites estimadas.
- Registrei o desenvolvimento e as decisões em 11 etapas.

---

## 🚨 Problema de Negócio

Uma diária pode parecer barata até que se considere o bairro, o espaço disponível e a capacidade do imóvel. Essas diferenças dificultam a escolha entre anúncios.

Usei os dados públicos do Inside Airbnb para investigar quanto essas características ajudam a estimar o preço anunciado. O projeto começou no contexto de Host Growth e chegou a uma aplicação de consulta para anfitriões e hóspedes.

Fiquei responsável pela preparação dos dados, comparação dos modelos e construção do simulador. A pergunta que orientou o trabalho foi quanto deveria ser a referência de diária para um anúncio com aquelas características.

---

## 🗺️ Planejamento da Solução

Organizei o trabalho em 11 etapas, seguindo uma adaptação do CRISP-DM.

1. Definição do problema preditivo e do snapshot.
2. Auditoria e limpeza dos dados, integração de fontes e congelamento das partições.
3. Engenharia de atributos de imóvel, localização, anfitrião e reputação.
4. Análise exploratória e investigação de valores extremos.
5. Seleção de features com Boruta, importância e análise de estabilidade.
6. Preparação dos dados em pipelines.
7. Comparação de algoritmos de regressão.
8. Ajuste de hiperparâmetros com Optuna e validação cruzada.
9. Avaliação histórica, referências de preço e faixas de incerteza.
10. Projeções econômicas sob hipóteses explícitas.
11. Persistência do pipeline em pickle e aplicação Streamlit.

Os registros completos estão em [docs/plans](./docs/plans).

Usei Python com pandas, NumPy, SciPy e matplotlib na análise, scikit-learn, Boruta, XGBoost, LightGBM e Optuna na modelagem, e Streamlit com Altair na aplicação. O desenvolvimento analítico está no JupyterLab.

---

## 🛠️ Desenvolvimento

### Dataset

| Item | Descrição |
|---|---|
| Fonte | Inside Airbnb, Amsterdam |
| Snapshot | 06/12/2018 |
| Base principal | `listings_details.csv` |
| Auxiliares | Avaliações e dados de bairros, incluindo GeoJSON |
| Granularidade de modelagem | Um registro por anúncio |
| Variável alvo | `price`, em euros por noite |
| Features finais | 36 |
| Desenvolvimento final | 17.021 anúncios |
| Avaliação histórica | 3.005 anúncios |

Mantive uma linha por anúncio e agreguei as avaliações por imóvel. Por isso, o calendário diário ficou fora da base de modelagem. Preservei o teste bruto em disco e ajustei os tratamentos dos dados apenas no conjunto de desenvolvimento.

### Modelagem e Fine Tuning

Comparei sete estimadores com as mesmas 36 features, usando 14.018 anúncios para treino e 3.003 para validação. O pré-processamento foi ajustado no treino. Também verifiquei a estabilidade das features e comparei diferentes subconjuntos de atributos.

#### Comparação inicial

| Modelo | MAPE em validação | MAE | RMSE |
|---|---:|---:|---:|
| DummyRegressor com média | 49,04% | € 63,01 | € 191,56 |
| DummyRegressor com mediana | 38,22% | € 59,42 | € 193,47 |
| Regressão linear | 31,91% | € 46,26 | € 178,91 |
| Regressão polinomial de grau 2 | 33,44% | € 47,73 | € 182,73 |
| Random Forest | 29,81% | € 44,16 | € 177,20 |
| XGBoost | **29,12%** | **€ 43,39** | € 178,99 |
| LightGBM | 29,43% | € 43,91 | **€ 174,54** |

Comecei com duas referências simples, prevendo a média ou a mediana para todos os anúncios. A regressão linear reduziu o erro, mas acrescentar termos polinomiais piorou o MAPE. Os menores erros percentuais vieram dos modelos de árvores.

XGBoost e LightGBM seguiram para o tuning. O XGBoost teve o menor MAPE inicial, e o LightGBM teve o menor RMSE e menor diferença de MAPE entre treino e validação. O ajuste levou 5,02 segundos para XGBoost e 2,12 segundos para LightGBM, frente a 60,76 segundos para Random Forest no ambiente do projeto.

#### Ajuste dos finalistas

Usei Optuna com amostrador TPE, 20 trials por algoritmo e validação cruzada de três folds no treino. Cada fold ajustou o pipeline completo, incluindo o pré-processamento.

| Configuração | MAPE em validação cruzada | MAPE em validação | MAE em validação | RMSE em validação |
|---|---:|---:|---:|---:|
| LightGBM fixo | 28,54% | 29,43% | € 43,91 | € 174,54 |
| LightGBM ajustado | **27,16%** | **27,77%** | **€ 41,68** | **€ 173,94** |
| XGBoost fixo | 27,85% | 29,12% | € 43,39 | € 178,99 |
| XGBoost ajustado | 27,74% | 28,13% | € 42,43 | € 176,15 |

O tuning reduziu o MAPE de validação do LightGBM em **1,66 ponto percentual** e o MAE em **€ 2,23**. No XGBoost, a redução foi de **1,00 ponto percentual** e **€ 0,97**. Após o ajuste, o LightGBM apresentou os menores MAPE, MAE e RMSE globais entre os finalistas e passou a ser a referência V2.

#### Modelo final

Na avaliação original do V2, ajustei o LightGBM nos **17.021 anúncios de desenvolvimento** e avaliei o pipeline nos **3.005 anúncios do teste histórico**. O V2 obteve **25,98% de MAPE**, **€ 38,95 de MAE** e **€ 105,32 de RMSE** nesse teste.

Salvei o pipeline treinado com o esquema de entrada e os metadados usados na inferência. A aplicação carrega esse artefato para calcular as referências de preço.

As comparações completas estão nos planos das [Etapas 07 V2](./docs/plans/plano-etapa-07-v2-machine-learning.md), [08 V2](./docs/plans/plano-etapa-08-v2-fine-tuning.md) e [09 V2](./docs/plans/plano-etapa-09-v2-metricas-recomendador.md).

### Funcionalidades do Simulador

- Formulário com características do imóvel e detalhes opcionais do anúncio.
- Lista de bairros com localização aproximada automática.
- Carregamento do pipeline treinado em pickle.
- Comparação entre diária informada e referência prevista.
- Diferença em euros e percentual, com mensagens curtas por faixa.
- Gráfico horizontal com duas barras e valores explícitos.
- Explicação da comparação em linguagem simples e faixa de referência disponível nos detalhes.

As mensagens usam limites de 10% e 25% de diferença em relação à previsão. Esses limites são regras de apresentação escolhidas para o produto.

### Estrutura do Projeto

```text
airbnb_price/
├── .streamlit/config.toml            # Tema da aplicação
├── app.py                            # Simulador de preços
├── assets/                           # Imagem e catálogo de bairros
├── data/                             # Dados brutos e partições
├── docs/plans/                       # Planos e evidências por etapa
├── models/
│   ├── airbnb_amsterdam_price_l1.pkl  # Pipeline usado pelo aplicativo
│   └── airbnb_amsterdam_price_v2.pkl  # Pipeline histórico
├── notebooks/
│   └── price_prediction.ipynb         # Desenvolvimento analítico
├── src/modeling/
│   └── inference.py                  # Validação, features e inferência
├── tests/                            # Verificações da inferência e app
├── pyproject.toml
├── requirements.txt
└── LICENSE
```

### Como Executar Localmente

Use Python entre 3.11 e 3.13. O ambiente local do projeto foi validado com Python 3.13.

No PowerShell, execute os comandos abaixo.

```powershell
git clone https://github.com/guigrandim/airbnb_price.git
cd airbnb_price

py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Abra o endereço informado no terminal, normalmente `http://localhost:8501`. O simulador carrega o artefato em `models/`. O catálogo de bairros em `assets/` permite usar a interface sem carregar os CSVs brutos.

Para abrir o ambiente de análise com os dados disponíveis localmente, execute o JupyterLab.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m jupyter lab
```

Para publicar no Streamlit Community Cloud, use o branch `main`, o arquivo `app.py` e Python **3.13**, selecionado em **Advanced settings** ao criar o app. O `requirements.txt` instala as dependências do simulador. O ambiente completo de análise está em `requirements-dev.txt`.

Se o app já foi criado com Python 3.14, recrie o deploy selecionando Python 3.13. Essa escolha é feita no painel do Community Cloud.

O desenvolvimento está no notebook [price_prediction.ipynb](./notebooks/price_prediction.ipynb).

---

## 💡 Top Insights

### 1. O histórico de avaliações muda a qualidade da estimativa

O MAPE foi de **24,27%** nos anúncios com histórico auxiliar e **37,18%** nos anúncios sem histórico. As estimativas para imóveis com pouca informação exigem mais cuidado.

### 2. O erro varia conforme o tipo de acomodação

Anúncios de espaço inteiro tiveram MAPE de **24,25%**, enquanto quartos privativos tiveram **32,62%**. Quartos compartilhados tiveram apenas seis registros na avaliação, uma amostra pequena para conclusões estáveis.

### 3. A faixa global perde cobertura nos imóveis mais caros

A faixa empírica incluiu o preço anunciado em **90,72%** dos casos. Entre os 25% de imóveis mais caros, essa cobertura caiu para **74,18%**.

As evidências estão no [plano da Etapa 09 V2](./docs/plans/plano-etapa-09-v2-metricas-recomendador.md).

---

## 📊 Resultados

### Modelo final usado no aplicativo

Mantive as 36 variáveis e troquei o objetivo do LightGBM por perda absoluta sem pesos. Na comparação com os mesmos cinco folds, o MAPE caiu de **27,17% para 23,30%** e o MAE de **€ 39,60 para € 37,57**. Acima de € 175, o MAPE passou de 23,62% para 24,53%. O peso intermediário atingiu 22,42% de MAPE global, com MAE de € 38,81 e MAPE de 27,42% acima de € 175.

O pickle do aplicativo foi ajustado nos 17.021 anúncios de desenvolvimento. A faixa empírica usa quantis dos resíduos fora do fold do próprio L1. As métricas do L1 são de validação cruzada no desenvolvimento. [Comparação e critérios de escolha](./docs/plans/plano-etapa-14-tres-alternativas-mape.md).

### Avaliação histórica do V2

| Indicador | Resultado |
|---|---:|
| Anúncios avaliados | 3.005 |
| MAPE | 25,98% |
| MAE | € 38,95 |
| RMSE | € 105,32 |
| Viés médio | −€ 1,16 |
| Cobertura da faixa empírica de 90% | 90,72% |

O MAPE é o erro percentual absoluto médio em relação ao preço anunciado. O MAE expressa a diferença absoluta média em euros por noite.

### O que foi entregue

Uma aplicação em que o usuário consegue comparar a diária de um anúncio com a referência do modelo antes de escolher uma acomodação. Ela mostra a diferença em euros e sinaliza quando vale pesquisar outras opções na base de Amsterdam de dezembro de 2018.

O modelo e as transformações ficam salvos no mesmo pipeline. Os testes conferem o esquema das features, as entradas do formulário e o resultado exibido na interface.

### Retorno do projeto e resultado econômico projetado

Na análise histórica do V2 com 20.026 anúncios, a aplicação das referências de preço às noites estimadas produziu um cenário anual de **€ 119,27 milhões em volume bruto de reservas**, frente a **€ 117,22 milhões** com os preços anunciados. A diferença projetada foi de **+€ 2,05 milhões**, mantendo constantes as noites estimadas.

| Indicador de negócio | Resultado do projeto |
|---|---|
| População analisada | 20.026 anúncios |
| Diferença anual projetada no volume bruto | +€ 2.053.631,79 |
| Variação sobre o volume bruto inicial | +1,75% |
| Decisão apoiada para o hóspede | Comparar a diária com uma referência e identificar preços acima ou abaixo dela |

Esse cenário mede a diferença de volume bruto ao trocar os preços anunciados pelas referências do modelo. Para calcular o ROI percentual, ainda é preciso incorporar a receita incremental da plataforma e os custos do projeto.

Os cálculos estão no [plano da Etapa 10 V2](./docs/plans/plano-etapa-10-v2-resultado-economico-final.md).

---

## ✅ Conclusões

O aplicativo usa LightGBM com perda absoluta sem pesos. A escolha reduziu o erro percentual e o erro absoluto médio na validação cruzada do desenvolvimento, com pequena piora no MAPE das diárias acima de € 175 frente ao V2.

**Limitações**

- Os dados representam dezembro de 2018. A aplicação tem finalidade de demonstração retrospectiva.
- O teste histórico já havia sido observado em versões anteriores do projeto, o que limita a interpretação de independência da avaliação final.
- A localização automática usa o centro aproximado do bairro, podendo alterar a previsão em relação às coordenadas exatas do imóvel.
- Há maior erro nos anúncios sem histórico e cobertura inferior da faixa entre imóveis caros.
- O alvo é o preço anunciado. A avaliação de preço ótimo e retorno realizado exige reservas, faturamento ou experimentos.

**Próximos passos**

- Avaliar uma safra recente com um novo conjunto de teste independente.
- Revisar a calibração das faixas de referência por segmento.
- Validar o uso do simulador com usuários e dados reais de reservas.

---

## 🧰 Skills Demonstradas

Regressão, qualidade de dados, feature engineering, seleção e estabilidade de atributos, pipelines, validação cruzada, otimização de hiperparâmetros, análise de resíduos, avaliação por segmento e desenvolvimento de produto de dados.

## 👩‍💻 Autor

Desenvolvido por **Guilherme Grandim** como projeto de portfólio em Ciência de Dados e Machine Learning.

[LinkedIn](https://www.linkedin.com/in/guilherme-grandim/) · [GitHub](https://github.com/guigrandim)

## 📄 Licença

Código disponibilizado sob a licença MIT. Consulte [LICENSE](./LICENSE). Os dados de origem seguem os termos da fonte Inside Airbnb.
