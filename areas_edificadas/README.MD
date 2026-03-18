# Criação de mapa de áreas edificadas a partir de edificado Lidar 2024

**Cartografia de áreas edificadas, i.e. áreas com mais de 10 edifícios que distem entre si menos de 50 m.**

## Input:

1. Ficheiro vetorial de polígonos de edificado Lidar (EPSG:3763)


## Scripts a executar em QGIS

Versão QGIS: QGIS 3.44.7; Versão Python: Python 3.12.12. Packages instalados: ver `requirements.txt`

1. Densificação dos vértices do input por forma que a distância seja inferior a 50 m e extração de vértices: `densify_by_interval_less_50m.py`
2. Determinação do grafo dos vértices que distam até 50 m e determinação de componentes conexas: `clusters_areas_edif_from_vertices_scipy_sparse.py`
3. Associar a cada feature do input o índice da componente conexa (`comp_id`), criando asim os clusters de edifícios que compõem cada área edificada: `associate_id_comp_to_polygons_area_edif.py`
4. Agrupar features por `comp_id` e obter features multipart (clusters de edifícios); input: `N=10`: `select_areas_edif_minimum_10.py`
5. Aplicar `convave hull` aos clusters de edifícios: usar QGIS plug-in `Concave Hull`
