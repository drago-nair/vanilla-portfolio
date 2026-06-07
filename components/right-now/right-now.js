(() => {
  customElements.define(
    "right-now",
    class RightNow extends HTMLElement {
      constructor() {
        super();
        this.innerHTML = '<span id="rn-time">--:--</span>';
        this.#tick();
        this._interval = setInterval(() => this.#tick(), 30_000);
      }

      disconnectedCallback() {
        clearInterval(this._interval);
      }

      #tick() {
        const el = this.querySelector("#rn-time");
        if (!el) return;
        const now = new Date();
        const time = now.toLocaleTimeString("en-IN", {
          timeZone: "Asia/Kolkata",
          hour: "2-digit",
          minute: "2-digit",
          hour12: false,
        });
        el.textContent = time;
      }
    }
  );

  appendStyle(
    "right-now",
    `<style>
      right-now {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 6px;
        text-align: center;
        font-style: italic;
      }
      right-now::before {
        content: "local time";
        font-size: 0.8em;
        opacity: 0.6;
      }
      right-now span {
        font-size: 2em;
        font-weight: bold;
        font-style: normal;
        color: var(--clr0-light, #4ade80);
      }
    </style>`
  );
})();
