# Etapa 03: Feature Engineering

**Status:** concluída; Etapa 04 aprovada e executada.

## Objetivo e base de entrada

Criar atributos interpretáveis sobre capacidade, anfitrião, reputação, localização e restrições de estadia, sem alterar a base da Etapa 02 nem consultar o teste reservado.

`df_modeling_final` tem 14.806 linhas e 23 colunas: `id`, `price`, 20 preditoras e `particao`. São 12.187 anúncios de treino e 2.619 de validação. `df_test_raw.csv` permanece bruto, com 3.005 linhas e 96 colunas.

## Atributos planejados e criados

Foram criadas 22 features. O dicionário completo, com fórmulas e ressalvas, está no notebook.

- Capacidade (4): `is_studio`, `bedrooms_per_guest`, `bathrooms_per_guest` e `accommodates_log1p`.
- Anfitrião, reputação e reserva (7): `host_tenure_years`, `host_listings_log1p`, `host_has_multiple_listings`, `number_of_reviews_log1p`, `reviews_per_month_log1p`, `is_superhost` e `is_instant_bookable`.
- Localização e interações (4): `room_type_neighbourhood`, `property_type_room_type`, `rating_x_superhost` e `distance_to_training_center_km`.
- Estadia e disponibilidade (7): `availability_full_year`, `availability_low`, `minimum_nights_log1p`, `minimum_nights_over_30`, `maximum_nights_log1p`, `maximum_nights_over_365` e `maximum_nights_equals_1125`.

## Regras contra vazamento

- `id`, `price` e `particao` não entram na lista de preditores. Não foram usados preços futuros, receita derivada do alvo ou target encoding.
- `host_tenure_years` usa a data fixa do snapshot, 06/12/2018. `availability_365` continua representando noites disponíveis, não ocupação.
- O centro espacial e as associações entre features foram calculados somente no treino. A validação recebeu as mesmas regras; o teste não foi lido nem transformado.
- Razões e logaritmos foram verificados para denominadores zero e valores negativos. Não houve novas ausências ou infinitos.

## Evidências e ressalvas

- A verificação final criou `df_modeling_features` com 14.806 linhas e 45 colunas: 20 preditoras originais, 22 novas features, `id`, `price` e `particao`. As colunas originais, IDs, ordem e partições foram preservados. A lista de preditores contém 42 colunas.
- A fonte permaneceu inalterada. O teste bruto continuou com 3.005 linhas e 96 colunas; seu arquivo local manteve 11.634.013 bytes.
- Há 806 anúncios com `bedrooms = 0`; `is_studio` indica essa condição, mas não confirma o tipo real do imóvel.
- No treino, 16 de 60 combinações de quarto e bairro tinham menos de 20 anúncios e cobriam 43 linhas. Para propriedade e quarto, eram 33 de 53 combinações e 158 linhas.
- O GeoJSON contém 22 geometrias `MultiPolygon` sem CRS declarado. Nenhum anúncio de desenvolvimento ficou fora dos limites. A distância criada usa o centro mediano do treino (52,3647; 4,8861) e é um proxy da amostra, não uma distância a um centro oficial.
- A flag `maximum_nights_equals_1125` vale 1 para 7.398 anúncios de desenvolvimento. Isso não comprova que 1.125 seja um default. `availability_low` vale 1 para 9.884 anúncios e não indica reservas.
- Sem `price`, no treino, foram encontrados 14 pares com |Spearman| >= 0,90 e 8 com |Pearson| >= 0,90. O maior Pearson foi 0,999638 entre `is_superhost` e `rating_x_superhost`. Essas features seguem como candidatas para comparação posterior.

## Resultado e gate

As 22 features ficam como candidatas. Esta etapa não treinou modelos nem calculou MAPE, portanto não há ganho preditivo confirmado. Redundância e categorias raras devem ser avaliadas nas etapas seguintes.

A Etapa 03 foi concluída antes da aprovação da Etapa 04.

Notebook: `notebooks/price_prediction.ipynb`.

## Registro da reconstrução do kernel

- Em 09/11/2026, a entrada da Etapa 03 foi reconstruída via MCP com 14.806 linhas, 23 colunas, 12.187 anúncios de treino e 2.619 de validação.
- A checagem de entrada confirmou presença e tamanho do arquivo do teste por metadados, sem carregar o CSV nessa célula.
- A célula final 03.6 não foi resolvida pelo executor MCP após a reinicialização. As verificações posteriores da Etapa 04 (incluindo o gate final) e da Etapa 06 confirmaram partições, features e integridade da base.
