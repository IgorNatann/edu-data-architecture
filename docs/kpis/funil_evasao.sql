/*
VIEW: vw_funil_evasao
DESCRICAO: Analisa o funil de evasao da escola por status de matricula.
CAMADA: Semantica (Consumo BI) / Schema: dw

CASO DE USO:
    "Qual a taxa de evasao e quanto de receita esta em risco?"
*/

CREATE OR REPLACE VIEW dw.vw_funil_evasao AS
WITH totais AS (
    SELECT COUNT(DISTINCT nk_matricula) AS total_geral
    FROM dw.fato_matricula
),
por_status AS (
    SELECT
        s.codigo_status,
        s.descricao_status,
        COUNT(DISTINCT f.nk_matricula)  AS total_matriculas,
        ROUND(SUM(f.valor_total), 2)    AS receita_envolvida,
        ROUND(
            SUM(f.valor_total) / NULLIF(COUNT(DISTINCT f.nk_matricula), 0),
        2)                              AS ticket_medio
    FROM dw.fato_matricula f
    JOIN dw.dim_status s ON f.sk_status = s.sk_status
    GROUP BY s.codigo_status, s.descricao_status
)
SELECT
    ps.codigo_status,
    ps.descricao_status,
    ps.total_matriculas,
    ROUND(
        ps.total_matriculas * 100.0 / NULLIF(t.total_geral, 0),
    1)                              AS percentual,
    ps.receita_envolvida,
    ps.ticket_medio,
    CASE
        WHEN ps.codigo_status IN ('Trancada', 'Cancelada') THEN TRUE
        ELSE FALSE
    END                             AS is_evasao
FROM por_status ps
CROSS JOIN totais t
ORDER BY ps.total_matriculas DESC;

/*
EXEMPLOS:
    SELECT * FROM dw.vw_funil_evasao;
    SELECT * FROM dw.vw_funil_evasao WHERE is_evasao = TRUE;
    SELECT SUM(percentual) AS taxa_evasao FROM dw.vw_funil_evasao WHERE is_evasao = TRUE;
*/
