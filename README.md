# 🏘️ Airbnb Amsterdam — Referência de Preços de Diárias

Modelo de machine learning e simulador em Streamlit para comparar o preço informado de uma acomodação com uma referência baseada em anúncios de Amsterdam de dezembro de 2018.

![Python](https://img.shields.io/badge/Python-3.11–3.13-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.67-FF4B4B?logo=streamlit&logoColor=white)
![LightGBM](https://img.shields.io/badge/Modelo-LightGBM-29804A)
![Licença](https://img.shields.io/badge/licença-MIT-green)

<p align="center">
<img src="./assets/amsterdam-night.png" alt="Ilustração fotográfica de Amsterdam ao anoitecer, gerada com IA para o cabeçalho do simulador" width="800">
</p>

### 🎯 Destaques

- Desenvolvi um pipeline LightGBM com **36 features**, com MAPE de **25,98%** e MAE de **€ 38,95** na avaliação histórica de **3.005 anúncios**.
- Entreguei um simulador que compara o preço informado com a referência estimada, apresenta a diferença em euros e usa um gráfico de duas barras para facilitar a leitura.
- Integrei localização por **22 bairros**, com coordenadas aproximadas preenchidas automaticamente a partir dos limites geográficos oficiais do dataset.
- Documentei o processo em **11 etapas**, incluindo qualidade dos dados, seleção de atributos, tuning, incerteza e cenários econômicos.

---

## 🚨 Problema de Negócio

Anfitriões e hóspedes precisam avaliar como o preço de uma diária se posiciona em relação a acomodações com características semelhantes. Capacidade, localização, tipo de imóvel e histórico de avaliações tornam essa comparação difícil quando feita apenas olhando anúncios individuais.

O projeto explora esse problema no contexto de Host Growth, usando dados públicos do Inside Airbnb e uma aplicação de consulta para tornar a comparação acessível.

**Pergunta central** — Qual preço de referência o modelo estima para um anúncio de Amsterdam a partir das características disponíveis?

**Minha tarefa** — Conduzir o processo de ciência de dados, avaliar modelos de regressão e transformar o pipeline treinado em um simulador de comparação de preços.

---

## 🗺️ Planejamento da Solução

O desenvolvimento seguiu um fluxo adaptado de **CRISP-DM**, com planos e decisões registrados por etapa.

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

**Ferramentas utilizadas** — Python, pandas, NumPy, SciPy, matplotlib, scikit-learn, Boruta, XGBoost, LightGBM, Optuna, Altair, JupyterLab e Streamlit.

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

O calendário diário foi excluído da construção da base de modelagem para preservar a granularidade por anúncio. As avaliações auxiliares foram agregadas por imóvel. O teste bruto foi preservado em disco, e os tratamentos aprendidos foram limitados ao desenvolvimento.

### Modelagem e Fine Tuning

Foram avaliados baselines, regressão linear e polinomial, Random Forest, XGBoost e LightGBM. A seleção incluiu análise de estabilidade das features e comparação de subconjuntos.

A tabela apresenta as configurações finalistas documentadas na Etapa 08 V2.

| Configuração | MAPE em validação | MAE em validação |
|---|---:|---:|
| LightGBM fixo | 29,43% | € 43,91 |
| LightGBM ajustado | **27,77%** | **€ 41,68** |
| XGBoost fixo | 29,12% | € 43,39 |
| XGBoost ajustado | 28,13% | € 42,43 |

O LightGBM ajustado foi escolhido pelo MAPE global e pelo MAE na validação. A busca utilizou Optuna, com orçamento de 20 trials por algoritmo finalista. O pipeline foi ajustado no conjunto de desenvolvimento e persistido com o esquema de entrada e metadados necessários à inferência.

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
│   └── airbnb_amsterdam_price_v2.pkl  # Pipeline treinado e metadados
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
.\.venv\Scripts\python.exe -m jupyter lab
```

O desenvolvimento está no notebook [price_prediction.ipynb](./notebooks/price_prediction.ipynb).

---

## 💡 Top Insights

### 1. O histórico de avaliações muda a qualidade da estimativa

O MAPE foi de **24,27%** nos anúncios com histórico auxiliar e **37,18%** nos anúncios sem histórico. Esse resultado orienta o cuidado necessário ao interpretar referências para imóveis com pouca informação disponível.

### 2. O erro varia conforme o tipo de acomodação

Anúncios de espaço inteiro tiveram MAPE de **24,25%**, enquanto quartos privativos tiveram **32,62%**. Quartos compartilhados tiveram apenas seis registros na avaliação, uma amostra pequena para conclusões estáveis.

### 3. A faixa global perde cobertura nos imóveis mais caros

A faixa empírica alcançou cobertura global de **90,72%**, mas apenas **74,18%** no quartil de maior preço. A avaliação por segmento revelou uma limitação que a métrica agregada esconderia.

As evidências estão no [plano da Etapa 09 V2](./docs/plans/plano-etapa-09-v2-metricas-recomendador.md).

---

## 📊 Resultados

### Avaliação Histórica do Modelo Final

| Indicador | Resultado |
|---|---:|
| Anúncios avaliados | 3.005 |
| MAPE | 25,98% |
| MAE | € 38,95 |
| RMSE | € 105,32 |
| Viés médio | −€ 1,16 |
| Cobertura da faixa empírica de 90% | 90,72% |

O MAPE é o erro percentual absoluto médio em relação ao preço anunciado. O MAE expressa a diferença absoluta média em euros por noite.

### Resultado da Entrega

A aplicação permite consultar o modelo por formulário e entender a diferença entre a diária informada e a referência calculada. O usuário escolhe o bairro e preenche as características conhecidas, recebe a previsão e visualiza a comparação em um gráfico simples.

O pipeline persistido reúne o modelo treinado e as transformações necessárias para reproduzir a inferência. Os testes do projeto cobrem o contrato das features, validações de entrada e o fluxo de comparação na interface.

---

## ✅ Conclusões

O projeto conecta a análise de dados de anúncios a um simulador de referência de diárias, com métricas globais, avaliação por segmento e documentação das decisões. A entrega permite explorar a resposta do modelo às características de uma acomodação e interpretar o preço informado dentro do contexto histórico utilizado.

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
