# Checklist de Deploy - CoopVale

## Antes do Deploy
- [ ] Revisar variáveis de ambiente (SECRET_KEY, configs de banco, debug=False)
- [ ] Garantir que todas as dependências estão no `requirements.txt`
- [ ] Testar todos os fluxos principais manualmente e rodar `pytest`
- [ ] Validar permissões de usuário (admin, produtor, cliente, visitante)
- [ ] Conferir responsividade e layout em desktop e mobile
- [ ] Conferir mensagens de erro e sucesso
- [ ] Remover dados de teste e criar usuários reais
- [ ] Configurar domínio e HTTPS (se for produção)
- [ ] Configurar backup do banco de dados
- [ ] Documentar instruções de uso e acesso para usuários finais

## Durante o Deploy
- [ ] Subir ambiente virtual e instalar dependências
- [ ] Executar migrações/criação de banco de dados
- [ ] Testar rotas principais no ambiente de produção
- [ ] Validar logs e monitoramento

## Pós-Deploy
- [ ] Monitorar erros e feedback dos usuários
- [ ] Fazer backup periódico
- [ ] Atualizar documentação conforme melhorias

---

## Ajustes Finais Recomendados
- [ ] Adicionar favicon e logo personalizados
- [ ] Revisar textos institucionais e de ajuda
- [ ] Implementar paginação em listas grandes
- [ ] Adicionar testes automatizados para fluxos críticos
- [ ] Configurar e-mail de contato/recuperação de senha
- [ ] Revisar segurança: CSRF, XSS, senhas, uploads
- [ ] Validar uploads de imagens (tamanho, formato)
- [ ] Otimizar queries e uso de banco
- [ ] Adicionar analytics (Google Analytics, etc.)
- [ ] Planejar rotina de atualização e manutenção
