# Biblioteca de Imagens de Espécies

Estrutura opcional para fotos locais (pastas legadas no banco; na UI tudo aparece junto em **Fotos da espécie**):

- `especies/arvores/<id_especie>.jpg`
- `especies/sementes/<id_especie>.jpg`
- `especies/folhas/<id_especie>.jpg`

O `id_especie` vem da tabela `especies` no banco. Qualquer JPG local válido entra na mesma galeria.

## Imagens via speciesLink (padrão)

Pipeline no sync: speciesLink → GBIF → iNaturalist (fallback por gênero se faltar). Exsiccatae/Reflora ignorados. Cache em `especies_biblioteca.imagens_externas`.

Sincronizar as 90 espécies:

```bash
docker compose exec api python scripts/sync_specieslink_imagens.py
```

Configure no `.env` do `api_viveiro`:

```env
SPECIESLINK_API_KEY=sua_chave_aqui
```

No modal da espécie, locais + cache externo são exibidos numa única galeria. No card da lista, usa a primeira foto disponível.
