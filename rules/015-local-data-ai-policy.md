# Política de Plataforma Local, Dados e IA

## Execução e orçamento

Use `policies/project-defaults.json` como fonte canônica dos padrões do kit.
A execução começa local. Nuvem é opcional para uso pessoal, com teto total de
R$ 100/mês em infraestrutura: compute, bancos, observabilidade, armazenamento,
backups, rede e encargos de câmbio/impostos. IA possui orçamento separado ainda
não quantificado; valor ausente não significa uso ilimitado ou autorização de gasto.

Registre fontes oficiais de preços, data, região, uso previsto, conversão para BRL
e encargos. Uma proposta sem informações essenciais não está pronta. A reserva
sugerida de R$ 20 serve ao planejamento, sem substituir o teto do usuário.
Respeite configurações explícitas de cada projeto e autorizações existentes.

## Ferramentas e adoção

Prefira ferramentas mantidas e estáveis, adequadas aos requisitos. Verifique e
fixe versões; não escolha preview apenas por ser recente. Ative serviços por
necessidade, preservando a stack do projeto. Consulte a documentação bilíngue
`docs/pt-br/local-platform-and-ai.md` e `docs/en/local-platform-and-ai.md`.

## Dados e IA

Defina schema, proprietário, qualidade, origem, privacidade, retenção e recuperação
antes de conectar consumidores de dados e IA. IA deve ter baseline, saída
estruturada, ferramentas limitadas, avaliações e fallback conforme o caso.
RAG, busca vetorial e modelos locais exigem requisito e avaliação, não são defaults.

Meça custo por tarefa aceita, incluindo retentativas e avaliações. Limite contexto,
tentativas, chamadas e tempo. Cache e uso dependem do cliente/provedor; ausência
de medição deve aparecer como indisponível, nunca como custo zero. Não prometa
economia de tokens sem comparação reproduzível e qualidade preservada.

## Escopo de implementação

Esta política orienta todos os papéis e acompanha suas skills portáveis. O
empacotador detecta divergência entre cópias; não impõe limites financeiros em
runtime. O executor deverá implementar configuração efetiva, limites e registros.
