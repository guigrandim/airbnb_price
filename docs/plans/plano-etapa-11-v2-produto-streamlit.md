# Etapa 11 V2 — Produto de dados em Streamlit

**Status:** autorizada pelo usuário após aprovação da Etapa 10 V2 em 15/11/2026. Desenho aprovado, com persistência do pipeline vencedor em pickle.

## Objetivo

Entregar uma interface local para estimar preço de referência dos anúncios de Amsterdam a partir de campos preenchidos pelo usuário, carregando o melhor pipeline já treinado e aprovado, sem retreinar a cada previsão.

## Escopo e contrato

- Artefato versionado `models/airbnb_amsterdam_price_v2.pkl`, criado via célula MCP a partir de `v209_final_pipeline`, selecionado na Etapa 08 e avaliado na Etapa 09 V2. Persistir pipeline sklearn/LightGBM em pickle junto de features ordenadas, quantis de resíduos OOF, data do snapshot, referência geográfica, janela de reviews, versões de bibliotecas e métricas de avaliação.
- O carregamento será somente de artefato local do projeto. Não aceitar upload de pickle externo.
- A aplicação em `app.py` carrega o artefato e coleta dados brutos necessários. `src/modeling/inference.py` converte os valores do formulário em uma linha nas 36 features aprovadas, mantendo a mesma ordem e fórmulas de treino.
- O contrato inclui somente os campos brutos que alimentam as36features aprovadas: capacidade/tipo de imóvel, bairro/coordenadas, anfitrião, avaliações e datas, disponibilidade/noites, preços adicionais, cancelamento e cama. Comodidades não estão no bloco selecionado `capacidade_comercial` e não serão pedidas na UI. Recência e tenure serão referidas ao snapshot06/12/2018. Validar datas futuras em relação ao snapshot, domínios numéricos e acomodação positiva. Categorias novas continuam permitidas pelo OneHotEncoder configurado com `handle_unknown='ignore'`.
- A UI mostra preço de referência, faixa empírica central de 90%, preço anunciado opcional, diferença de referência e avisos sobre snapshot histórico, holdout previamente observado e cobertura desigual. Previsões brutas não positivas resultam em abstenção. Nenhuma saída será chamada de preço ótimo.
- O cenário financeiro será apenas ilustrativo e não transformará gaps em receita ou ROI. Incluir os limites de uso e exigir validação causal para retorno.
- Fixar Streamlit e dependências de runtime em `requirements.txt`; documentar ambiente e comando local de inicialização na documentação existente.
- `tests/test_inference.py` verificará fórmulas determinísticas, preservação de ausências, data de referência, validações e schema de36features. Casos de integração conferirão round-trip pickle, previsão típica, categorias novas, ausências aceitas pelo pipeline e coerência com o notebook.

## Células previstas no notebook

- `## Etapa 11 — Produto de Dados em Streamlit`, com aprovação da etapa10V2 e limites do produto.
- `### 11.1 — Verificação do modelo e contrato`: kernel, pipeline congelado, esquema, quantis e versões; nenhuma chamada `fit` ou `predict`.
- `### 11.2 — Persistência do modelo`: empacotar metadados e salvar o melhor pipeline em pickle via MCP; reabrir o artefato e conferir hash e parâmetros.
- `### 11.3 — Conferência notebook/app`: vetorizar um exemplo usando a mesma engenharia do módulo da aplicação e comparar entrada do pipeline/previsão.
- `### 11.4 — Auditoria e gate`: caminho/hash/versionamento do artefato e integridade dos objetos do notebook.

## Ordem de implementação

1. Inspecionar via MCP o schema exato, fórmulas, categorias e versões do kernel; congelar manifesto do artefato.
2. Escrever testes de inferência e observar falha esperada.
3. Implementar módulo de engenharia/inferência e passar os testes.
4. Gerar pickle contendo pipeline e manifesto por célula MCP; conferir leitura por `pickle` e assinatura de features.
5. Implementar frontend com controles válidos, cálculo e apresentação da incerteza e limites.
6. Instalar dependências somente na `.venv`, validar os fluxos previstos e documentar execução local.
7. Salvar/inspecionar células via MCP, revisar consistência notebook–app, atualizar este plano com evidências e registrar o gate.

## Critérios de aceite

- Artefato pickle contém o pipeline V2 congelado e manifesto reproduzível; aplicação não faz treino.
- Uma entrada bruta gera exatamente as 36 colunas ordenadas esperadas, sem `id`, alvo ou partição.
- Features derivadas (tenure, recência, razões, comodidades e distância) reproduzem as regras aprovadas, usando o snapshot e centro fixos.
- Nulos opcionais são tratados pelo pipeline. Categorias novas são aceitas; valores inválidos e datas posteriores ao snapshot são explicados ao usuário.
- Caso típico retorna preço de referência e intervalo; previsão não positiva gera abstenção.
- Saída do app coincide com a do pipeline em notebook para mesmo exemplo. Teste de execução do Streamlit mostra a interface sem falhas.
- Avisos separam preço anunciado histórico, inferência indicativa e projeção financeira; não há alegação de causalidade, ROI observado ou faixa individual garantida.
- Documentação dá comando exato de ativação/execução e dependências fixadas.
- Notebook e bruto continuam íntegros; plano e seção final registram decisões, pendências e último gate.

## Riscos e limites conhecidos

O modelo foi treinado em snapshot de 2018 e o teste histórico já havia sido observado no fluxo do projeto. A faixa empírica teve cobertura de 90,72% no teste e cobertura inferior no quartil caro (74,18%) e sem reviews (81,66%). O produto serve como demonstração retrospectiva. Não serve como recomendação operacional para o mercado atual sem nova safra e validação.

O artefato pickle só deve ser carregado a partir do repositório local de confiança. O módulo exige a mesma versão principal de Python e versões idênticas de scikit-learn e LightGBM; a carga entre Python 3.10 e 3.13 foi validada no ambiente do projeto.

## Gate

### Implementação e evidências

- `models/airbnb_amsterdam_price_v2.pkl` contém o pipeline vencedor V2 e o manifesto; tamanho `1.402.042` bytes; SHA-256 `408b41b18a2ca37982f4cc7ac03628c7675507dca1b7d410357f1b9b434028f7`.
- A célula MCP 334 reabriu o pickle, conferiu parâmetros do LightGBM, schema ordenado das 36 features e comparou a engenharia e previsão com uma linha de treino: notebook e app coincidiram; não houve retreino nem acesso ao teste.
- `src/modeling/inference.py` implementa validação e transformação de campos do formulário para as 36 features, carrega o pickle e entrega preço de referência/faixa. `app.py` usa `st.cache_resource`, aceita dados do anúncio, apresenta comparação com preço informado e cenário financeiro ilustrativo.
- `.venv` foi atualizada para Python `3.13.17`; Streamlit `1.67.0`; JupyterLab `4.6.4`; ipykernel `7.2.0`; Jupyter Server MCP `0.4.0`; scikit-learn `1.7.2`; LightGBM `4.7.0`. O artefato registra Python de treinamento `3.10.4`; a inferência cruzada entre esses runtimes passou. A reinstalação revelou que processos Jupyter antigos bloqueavam dependências; eles foram encerrados depois de salvar o notebook, e as ferramentas Jupyter/MCP foram acrescentadas a `requirements.txt`.
- `jupyter server extension list` validou `jupyter_server_mcp 0.4.0`; o comando `jupyter-server-mcp-proxy` foi recriado. Após o encerramento dos processos antigos, a conexão MCP desta sessão ainda respondeu `Transport closed`; precisa ser restabelecida ao reiniciar Codex/JupyterLab usando a nova `.venv`.
- `python -m pip check`: sem dependências quebradas. `python -m unittest discover -s tests -v`: `7/7` testes aprovados, incluindo carga real do pickle e envio do formulário com retorno de previsão. O servidor Streamlit local respondeu HTTP `200` em `/` e `/_stcore/health` no endereço `127.0.0.1`.
- `docs/docs/getting-started.md` documenta ambiente e inicialização com `streamlit run app.py`. `pyproject.toml` declara suporte de Python `>=3.11,<3.14`.
- Limitações mantidas: snapshot de 06/12/2018; teste histórico já observado pelo projeto; faixa empírica não garante cobertura individual; estimativa não representa preço ótimo, mercado atual, receita observada ou ROI realizado.

**Status:** Etapa 11 aprovada pelo usuário em 15/11/2026; gate do projeto aprovado.

**Sincronização do notebook:** após reiniciar Codex/Jupyter, usei os comandos Jupyter MCP `get-notebook-info`, `get-cell-info`, `set-cell-content`, `run-cell` e `docmanager:save`. A célula final foi executada e salva, registrando Etapa 11 aprovada, Etapa 11 como última etapa aprovada, decisão de usar o pipeline V2 salvo em pickle, limite do snapshot de 06/12/2018 e ausência de pendências para encerramento.
