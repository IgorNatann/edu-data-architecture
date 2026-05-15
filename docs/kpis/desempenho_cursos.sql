/*
=============================================================================
VIEW: vw_desempenho_cursos
DESCRICAO: Analisa o desempenho comercial de cada curso oferecido pela escola.
CAMADA: Semantica (Consumo BI)
SCHEMA: dw

METRICAS ENTREGUES:
    - total_inscricoes: Quantidade de vezes que o curso aparece em matriculas.
    - total_matriculas_distintas: Matriculas unicas que incluem o curso.
    - receita_gerada: Soma dos valores das matriculas que incluem o curso.
    - ticket_medio_curso: Valor medio pago por matricula que inclui o curso.
    - preco_catalogo: Preco atual do curso no catalogo (para comparacao).
    - carga_horaria: Carga horaria do curso.
    - receita_por_hora: Receita total dividida pela carga horaria (eficiencia).

CASO DE USO:
    Responde a perguntas como:
    "Quais cursos geram mais receita?"
    "Qual curso tem melhor relacao receita/hora?"
    "Quais cursos sao mais populares?"

GRANULARIDADE: Uma linha por curso.
=============================================================================
*/

CREATE OR REPLACE VIEW dw.vw_desempenho_cursos AS
SELECT
    c.sk_curso,
    c.nome_curso,
    c.carga_horaria,
    c.preco_catalogo,
    COUNT(*)                                AS total_inscricoes,
    COUNT(DISTINCT f.nk_matricula)          AS total_matriculas_distintas,
    ROUND(SUM(f.valor_total), 2)            AS receita_gerada,
    ROUND(
        SUM(f.valor_total) / NULLIF(COUNT(DISTINCT f.nk_matricula), 0),
    2)                                      AS ticket_medio_curso,
    ROUND(
        SUM(f.valor_total) / NULLIF(c.carga_horaria, 0),
    2)                                      AS receita_por_hora
FROM dw.fato_matricula f
JOIN dw.dim_curso c ON f.sk_curso = c.sk_curso
GROUP BY c.sk_curso, c.nome_curso, c.carga_horaria, c.preco_catalogo
ORDER BY receita_gerada DESC;

/*
=============================================================================
EXEMPLOS DE CONSULTA:
    SELECT * FROM dw.vw_desempenho_cursos ORDER BY receita_gerada DESC;
    SELECT * FROM dw.vw_desempenho_cursos ORDER BY receita_por_hora DESC LIMIT 5;
    SELECT nome_curso, total_inscricoes FROM dw.vw_desempenho_cursos WHERE total_inscricoes > 10;
=============================================================================
*/
