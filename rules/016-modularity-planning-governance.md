# Modularidade e Governança de Planejamento

## Fronteiras e extensões

Mantenha conceitos do domínio independentes de SDKs e serviços específicos.
Integrações implementam contratos de capacidade, resultado, configuração e versão.
Prefira um monólito modular local; extraia processos/serviços quando houver requisito
ou carga observados. A linguagem do executor não determina a stack do projeto.

Novas extensões exigem necessidade demonstrada, registro explícito, compatibilidade,
configuração válida, limites de acesso e conformidade antes da ativação. Manifestos
não concedem autorização e código in-process não é sandbox. MCP pode conectar
ferramentas externas; ele não substitui políticas ou o executor.

## Decisões e planejamento

Use sessões quando houver decisão ou perspectivas a conciliar. Selecione apenas
papéis pertinentes e defina limites de rodadas/chamadas/tempo e orçamento de IA.
Reutilize evidências e preserve incertezas; não invente consenso. A sessão entrega
decisões propostas/adotadas/adiadas e ações com dono, aceite e dependências.

Decisões adotadas devem referenciar autoridade existente, sem repetir aprovações
já concedidas. Ações prontas exigem IDs reais e decisões válidas. Criar documentos
não equivale a criar issues, instalar ferramentas, publicar ou executar tarefas.
O executor deve conferir referências, ciclos, capacidades e política efetiva.

## Evidência de compatibilidade e evolução

Registre formato, cliente/versão, descoberta, capacidades, comportamento e resultados
de avaliações separadamente. Não declare otimização por estrutura de diretórios.
Novos provedores/tecnologias precisam preservar aceite, recuperação e limites.

Planeje IDs/configuração por projeto e contratos evolutivos desde o primeiro fluxo.
Isolamento entre clientes, cotas e cobrança entram antes de operação comercial.
O teto pessoal de infraestrutura não é uma promessa de custo para clientes futuros.
Consulte os guias bilíngues de plataforma modular, planejamento e compatibilidade.
