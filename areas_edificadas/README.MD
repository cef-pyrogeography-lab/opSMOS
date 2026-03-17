# Criação de mapa de áreas edificadas a partir de edificado Lidar 2024

**Cartografia de áreas edificadas, i.e. áreas com mais de 10 edifícios que distem entre si menos de 50 m.**

## Input:

1. Ficheiro vetorial de polígonos de edificado Lidar (EPSG:3763)


## Scripts:
1. Densificação dos vértices do input por forma que a distância seja inferior a 50 m e extração de vértices
2. Determinação do grafo dos vértices que distam até 50 m e determinação de componentes conexas 
3. Associar a cada feature do input o índice da componente conexa (`comp_id`), criando asim os clusters de edifícios que compõem cada área edificada
4. Agrupar features por `comp_id` 
