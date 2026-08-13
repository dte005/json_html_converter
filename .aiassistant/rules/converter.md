---
apply: always
---

# .aiassistant/rules/converter.md

## Stack
- Python 3.12+

## Contexto do projeto
### Objetivo
Ler arquivos de uma página HTML (incluindo CSS, JS e imagens associadas), identificar
suas seções conforme as REGRAS abaixo, extrair o HTML de cada seção **preservando
a estrutura e o conteúdo original** (tags, atributos e texto — não converter para
texto puro), minificar esse HTML, e salvar tudo em um JSON seguindo a estrutura
definida.

### CSS e JS
Arquivos .css e .js **não são extraídos nem embutidos no JSON**. Servem apenas de
contexto para localizar arquivos de imagem referenciados nas seções.

### Sections
Hoje o documento é dividido em várias seções determinadas por números.
Para cada seção encontrada um objeto é incluído em "sections".
Algumas seções que não possuem número são: Description, Document Approvals, entre
outras — essas ainda entram no array `sections`, identificadas pelo `title`,
com `id` gerado conforme a regra de geração de ID abaixo.

### Estrutura do json de saída
```json
{
  "header": {
    "doc_title": "",
    "document": "",
    "owner": "",
    "collection": "",
    "review_by": "",
    "revised": "",
    "effective": ""
  },
  "sections": [
    {
      "id": "",
      "title": "",
      "content": "",
      "attachments": [{
        "filename": "",
        "mime_type": "",
        "base64": ""
      }]
    }
  ],
  "approvals": [{
    "date": "",
    "by": ""
  }],
  "attachments": [{
    "filename": "",
    "mime_type": "",
    "base64": ""
  }]
}
```
1. `header`: dados do cabeçalho do documento.
2. `sections`: todas as seções, numeradas ou não.
   - `content`: string contendo o HTML **minificado** da seção.
   - `attachments`: imagens usadas dentro dessa seção específica, em base64.
3. `attachments` (raiz): imagens associadas ao header ou sem seção definida.

## Regras
- Todos os arquivos de origem estão em `input/`.
- CSS, JS e imagens ficam na mesma pasta do `.html` correspondente.
- O `content` de cada seção deve conter o HTML da seção **minificado**: sem
  espaços, tabulações ou quebras de linha desnecessárias entre tags.
  A estrutura (tags, atributos, texto visível) deve permanecer intacta —
  minificar não significa alterar conteúdo, apenas remover espaçamento
  não-semântico.
- A minificação deve ser feita com uma biblioteca dedicada (ex: `minify-html`),
  nunca com regex manual — evita corromper texto dentro de `<pre>`, `<script>`
  ou `<textarea>`, onde espaços são semânticos.
- O `id` de cada seção segue o número que aparece à esquerda do título no HTML
  original (ex: "3. Scope" → `id: "3"`).
- Para seções sem número à esquerda (ex: "Description", "Document Approvals"),
  gerar um `id` numérico aleatório, garantindo que nunca colida com um `id`
  já usado no mesmo documento (nem com os números reais de outras seções,
  nem com outro `id` gerado anteriormente no mesmo processamento).
- O `id`, numerado ou gerado, é sempre representado como **string** no JSON
  de saída (ex: `"3"`, `"482"`), para manter o tipo consistente entre os dois casos.
- Não modificar arquivos em `input/`.
- Um JSON é gerado por arquivo `.html`, salvo em `output/` com o mesmo nome
  do `.html` de origem (ex: `pagina.html` → `pagina.json`).
- Toda imagem referenciada em `<img>` deve ser convertida para base64 e
  incluída no array `attachments` correspondente (da seção ou da raiz).
- Se o arquivo de imagem referenciado não existir em disco, define o objeto
  com `"base64": null` e mantém `filename`/`mime_type` preenchidos — nunca
  interrompe o processamento do restante do documento.
- Encoding sempre UTF-8, `ensure_ascii=False` na serialização.

## Convenções de código
- Sempre usar abordagem orientada a objetos.
- Usar `pathlib`, nunca `os.path`.
- Funções e métodos com type hints.

## Convenções de estrutura de pastas
- Toda lógica de programação vive em `src/converter/`.
- `main.py` fica na raiz do source apenas para expor o serviço de conversão
  (não contém lógica de negócio).
- `converter/converter.py` centraliza a orquestração do processo principal
  (chama as classes de `lib/` na ordem correta).
- `converter/lib/` contém as classes de domínio, uma por arquivo:
  - `html_reader.py` → `HtmlReader`: carrega e faz o parsing do `.html`.
  - `section_extractor.py` → `SectionExtractor`: identifica e separa as seções,
    incluindo a atribuição de `id` (numerado ou gerado).
  - `html_minifier.py` → `HtmlMinifier`: recebe HTML bruto de uma seção e
    retorna a versão minificada.
  - `image_encoder.py` → `ImageEncoder`: resolve caminho e converte imagem
    em base64.
  - `json_writer.py` → `JsonWriter`: monta o dict final e salva em `output/`.