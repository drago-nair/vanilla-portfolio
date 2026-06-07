(() => {
  customElements.define(
    "right-now",
    class RightNow extends HTMLElement {
      constructor() {
        super();
        this.innerHTML = '<span id="rn-time">--:--</span><span id="rn-activity"></span>';
        this.#tick();
        this._interval = setInterval(() => this.#tick(), 30_000);
      }

      disconnectedCallback() {
        clearInterval(this._interval);
      }

      #tick() {
        const timeEl = this.querySelector("#rn-time");
        const actEl = this.querySelector("#rn-activity");
        if (!timeEl || !actEl) return;
        const now = new Date();
        const time = now.toLocaleTimeString("en-IN", {
          timeZone: "Asia/Kolkata",
          hour: "2-digit",
          minute: "2-digit",
          hour12: false,
        });
        timeEl.textContent = time;
        actEl.textContent = this.#getActivity();
      }

      #getActivity() {
        const now = new Date();
        const ist = new Date(now.toLocaleString("en-US", { timeZone: "Asia/Kolkata" }));
        const day = ist.getDay();
        const h = ist.getHours();
        const m = ist.getMinutes();
        const t = h + m / 60;

        // Work: Mon-Fri 10:00-19:00
        if (day >= 1 && day <= 5 && t >= 10 && t < 19) return "working 👨‍💻";

        // Gym: Mon-Sat 21:30-23:00
        if (day >= 1 && day <= 6 && t >= 21.5 && t < 23) return "at the gym 💪";

        // Running: Tue/Thu 16:00-17:00
        if ((day === 2 || day === 4) && t >= 16 && t < 17) return "out running 🏃";

        // Running: Sun 19:30-20:30
        if (day === 0 && t >= 19.5 && t < 20.5) return "out running 🏃";

        // Football: Fri 00:00-02:00
        if (day === 5 && t >= 0 && t < 2) return "playing football ⚽";

        // Gaming: Sat/Sun 00:00-03:00
        if ((day === 6 || day === 0) && t >= 0 && t < 3) return "gaming 🎮";

        const funny = [
          "probably breaking something",
          "chasing bugs in the dark",
          "staring at the ceiling",
          "questioning life choices",
          "hunting zero-days in dreams",
          "recharging the batteries",
          "listening to music too loud",
          "pretending to be AFK",
        ];
        return funny[Math.floor(Math.random() * funny.length)];
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
      right-now span:first-of-type {
        font-size: 2em;
        font-weight: bold;
        font-style: normal;
        color: var(--clr0-light, #4ade80);
      }
      right-now span:last-of-type {
        font-size: 0.85em;
        font-style: italic;
        opacity: 0.7;
        max-width: 200px;
        line-height: 1.3;
      }
    </style>`
  );
})();
