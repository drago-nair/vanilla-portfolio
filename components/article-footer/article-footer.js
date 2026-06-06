import("/components/article-reactions/article-reactions.js");

customElements.define(
  "article-footer",
  class ArticleFooter extends HTMLElement {
    constructor() {
      super();

      this.innerHTML = html`
        ${renderSig()}
        <div>
          <article-reactions></article-reactions>
        </div>
        ${maybeRenderSuggestions()}
      `;

      appendStyle(
        this.tagName,
        html`<style>
          article-footer {
            display: block;
            margin: auto;
            width: 100%;
            box-sizing: border-box;

            blockquote {
              margin: 60px auto;
              position: relative;
              padding: 0 18px;
              width: 100%;
              max-width: 700px;
              box-sizing: border-box;
              line-height: 21px;

              &::before {
                content: "❝";
                position: absolute;
                left: -15px;
                top: 0;
                font-size: 60px;
                opacity: 0.2;
              }
              a {
                font-weight: bold;
              }
              cite {
                white-space: nowrap;
                img {
                  position: relative;
                  top: 3px;
                }
              }
            }

            blockquote + div {
              display: flex;
              flex-wrap: wrap;
              align-items: stretch;
              gap: 24px;
              margin: 60px auto;
              padding: 0 18px;
              width: 100%;
              max-width: 900px;
              box-sizing: border-box;

              > * {
                flex: 1 1 350px;
              }
            }

            article-suggestions {
              margin: 120px auto;
            }
          }
        </style>`
      );
    }
  }
);

function renderSig() {
  const path = window.location.pathname;

  const introClause = html`Thanks for reading! `;
  const guestbookClause = html`Before you go, drop a note in
    <a href="/guestbook/">the guestbook</a>! `;
  const closingClause = html`Stay curious.
    <cite><i>&mdash;Vish</i></cite>`;

  let body = "";
  if (path.startsWith("/notes/")) {
    body = html`I write about cybersecurity, networking, and the
      <a href="/notes/">tools I build</a>. Sometimes I break things
      just to understand them. `;
  } else if (path.startsWith("/wares/")) {
    body = html`I build <a href="/wares/">security tools</a> and
      experiments — from network intrusion detection to
      hack-the-box challenges. `;
  } else {
    body = html`I'm a cybersecurity geek who <a href="/wares/">builds things</a>,
      breaks things, and writes about the journey. Welcome to my corner of the web. `;
  }

  return html`<blockquote>
    ${introClause}${body}${guestbookClause}${closingClause}
  </blockquote>`;
}

function maybeRenderSuggestions() {
  if (!window.location.pathname.startsWith("/notes/")) return "";
  import("/components/article-suggestions/article-suggestions.js");
  return html`<article-suggestions></article-suggestions>`;
}
