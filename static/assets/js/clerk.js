import './style.css'
import javascriptLogo from './javascript.svg'
import viteLogo from '/vite.svg'
import { setupCounter } from './counter.js'

document.querySelector('#app').innerHTML = `
  <div>
    <a href="https://vitejs.dev" target="_blank">
      <img src="${viteLogo}" class="logo" alt="Vite logo" />
    </a>
    <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript" target="_blank">
      <img src="${javascriptLogo}" class="logo vanilla" alt="JavaScript logo" />
    </a>
    <h1>Hello Vite!</h1>
    <div class="card">
      <button id="counter" type="button"></button>
    </div>
    <p class="read-the-docs">
      Click on the Vite logo to learn more
    </p>
  </div>
`

setupCounter(document.querySelector('#counter'))
import Clerk from "@clerk/clerk-js";
 
const clerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;
 
const clerk = new Clerk(clerkPubKey);
await clerk.load();
 
if (clerk.user) {
  document.getElementById("app").innerHTML = `
    <div id="user-button"></div>
  `;
 
  const userButtonDiv =
    document.getElementById("user-button");
 
  clerk.mountUserButton(userButtonDiv);
} else {
  document.getElementById("app").innerHTML = `
    <div id="sign-in"></div>
  `;
 
  const signInDiv =
    document.getElementById("sign-in");
 
  clerk.mountSignIn(signInDiv);
}