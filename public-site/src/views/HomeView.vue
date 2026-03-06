<script setup lang="ts">
</script>

<template>
  <div class="home">
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-content">
        <pre class="ascii-logo">
   ██████╗ ██████╗ ██╗     ██████╗  ██████╗ █████╗ ███████╗███████╗
  ██╔════╝██╔═══██╗██║     ██╔══██╗██╔════╝██╔══██╗██╔════╝██╔════╝
  ██║     ██║   ██║██║     ██║  ██║██║     ███████║███████╗█████╗
  ██║     ██║   ██║██║     ██║  ██║██║     ██╔══██║╚════██║██╔══╝
  ╚██████╗╚██████╔╝███████╗██████╔╝╚██████╗██║  ██║███████║███████╗
   ╚═════╝ ╚═════╝ ╚══════╝╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝
        </pre>
        <h1 class="tagline">Can You Solve What They Couldn't?</h1>
        <p class="subtitle">AI-powered interactive cold case investigations. Interrogate suspects. Analyze evidence. Crack the case.</p>
        <a href="http://localhost:4200" class="cta-button">&gt; ACCESS THE TERMINAL</a>
      </div>
    </section>

    <!-- Featured Cases -->
    <section class="section">
      <h2 class="section-title">&gt; FEATURED CASES</h2>
      <div class="cases-grid">
        <div class="case-card" v-for="c in cases" :key="c.id">
          <div class="case-number">{{ c.number }}</div>
          <div class="case-title">{{ c.title }}</div>
          <div class="case-meta">{{ c.era }} | {{ c.mood }}</div>
          <div class="case-synopsis">{{ c.synopsis }}</div>
        </div>
      </div>
    </section>

    <!-- How It Works -->
    <section class="section">
      <h2 class="section-title">&gt; HOW IT WORKS</h2>
      <div class="steps">
        <div class="step" v-for="step in steps" :key="step.num">
          <div class="step-number">{{ step.num }}</div>
          <div class="step-title">{{ step.title }}</div>
          <div class="step-desc">{{ step.desc }}</div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
      <p>ColdCase AI &mdash; Built with .NET, Spring Boot, FastAPI, Angular &amp; Vue.js</p>
    </footer>
  </div>
</template>

<script lang="ts">
export default {
  data() {
    return {
      cases: [
        { id: 1, number: 'CASE #1977-B', title: 'THE LAKE HOUSE', era: '1970s', mood: 'dark, foggy', synopsis: 'A body found in a lake near a wealthy family\'s estate.' },
        { id: 2, number: 'CASE #2003-K', title: 'DIGITAL GHOST', era: '2000s', mood: 'sterile, neon', synopsis: 'A programmer found dead, laptop wiped clean.' },
        { id: 3, number: 'CASE #1992-R', title: 'THE LAST BROADCAST', era: '1990s', mood: 'eerie, nostalgic', synopsis: 'A radio host vanishes mid-show.' },
      ],
      steps: [
        { num: '01', title: 'PICK A CASE', desc: 'Browse the cold case database and choose your investigation.' },
        { num: '02', title: 'INVESTIGATE', desc: 'Interrogate AI suspects, analyze evidence, visit the forensics lab.' },
        { num: '03', title: 'SOLVE', desc: 'File your case report and see how your deduction stacks up.' },
      ],
    }
  }
}
</script>

<style scoped>
.home {
  min-height: 100vh;
  background: #0a0a0a;
  color: #00ff41;
  font-family: 'Courier New', 'Lucida Console', monospace;
}

.hero {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 80vh;
  text-align: center;
  padding: 40px 20px;
}

.ascii-logo {
  font-size: 10px;
  line-height: 1.2;
  color: #00ff41;
  margin-bottom: 30px;
  overflow-x: auto;
}

.tagline {
  font-size: 2rem;
  margin-bottom: 16px;
  color: #00ff41;
}

.subtitle {
  font-size: 1rem;
  color: #00aa2a;
  margin-bottom: 40px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.cta-button {
  display: inline-block;
  padding: 16px 40px;
  border: 2px solid #00ff41;
  color: #00ff41;
  font-family: 'Courier New', monospace;
  font-size: 1.2rem;
  text-decoration: none;
  transition: all 0.3s;
}

.cta-button:hover {
  background: #00ff41;
  color: #0a0a0a;
}

.section {
  padding: 60px 40px;
  max-width: 1200px;
  margin: 0 auto;
}

.section-title {
  font-size: 1.4rem;
  margin-bottom: 30px;
  color: #ffb000;
}

.cases-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.case-card {
  border: 1px solid #00aa2a;
  padding: 24px;
  background: #0d0d0d;
  transition: border-color 0.3s;
}

.case-card:hover {
  border-color: #00ff41;
}

.case-number {
  font-size: 0.8rem;
  color: #ffb000;
  margin-bottom: 8px;
}

.case-title {
  font-size: 1.2rem;
  margin-bottom: 8px;
}

.case-meta {
  font-size: 0.85rem;
  color: #00aa2a;
  margin-bottom: 12px;
}

.case-synopsis {
  font-size: 0.9rem;
  color: #888;
}

.steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 32px;
}

.step {
  text-align: center;
}

.step-number {
  font-size: 2.5rem;
  color: #00d4ff;
  margin-bottom: 12px;
}

.step-title {
  font-size: 1.1rem;
  margin-bottom: 8px;
  color: #00ff41;
}

.step-desc {
  font-size: 0.9rem;
  color: #00aa2a;
}

.footer {
  text-align: center;
  padding: 30px;
  color: #555;
  font-size: 0.85rem;
  border-top: 1px solid #1a1a1a;
}
</style>
