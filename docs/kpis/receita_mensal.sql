/*
=============================================================================
VIEW: vw_receita_mensal
DESCRICAO: Consolida a receita mensal da instituicao, agrupando por ano e mes.
CAMADA: Semantica (Consumo BI)
SCHEMA: dw

METRICAS ENTREGUES:
    - total_matriculas: Quantidade de matriculas distintas no periodo.
    - receita_total: Soma dos valores totais das matriculas.
    - ticket_medio: Valor medio por matricula (Receita / Matriculas).
    - cursos_vendidos: Total de itens (cursos) vendidos no periodo.

CASO DE USO:
    Responde diretamente a pergunta da Diretoria:
    "Qual a receita mensal e o ticket medio da escola?"

GRANULARIDADE: Uma linha por combinacao ano + mes.
=============================================================================
*/

CREATE OR REPLACE VIEW dw.vw_receita_mensal AS
SELECT
    t.ano,
    t.mes,
    t.nome_mes,
    t.trimestre,
    COUNT(DISTINCT f.nk_matricula)  AS total_matriculas,
    SUM(f.valor_total)              AS receita_total,
    ROUND(
        SUM(f.valor_total) / NULLIF(COUNT(DISTINCT f.nk_matricula), 0),
    2)                              AS ticket_medio,
    COUNT(*)                        AS cursos_vendidos
FROM dw.fato_matricula f
JOIN dw.dim_tempo t ON f.sk_tempo = t.sk_tempo
GROUP BY t.ano, t.mes, t.nome_mes, t.trimestre
ORDER BY t.ano, t.mes;

/*
=============================================================================
EXEMPLO DE CONSULTA:
    SELECT * FROM dw.vw_receita_mensal ORDER BY ano, mes;
    SELECT * FROM dw.vw_receita_mensal WHERE ano = 2024;
=============================================================================
*/
