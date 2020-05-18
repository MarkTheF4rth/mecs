<template>
  <div id="app">
    <div class="container">
      <div class="columns">
        <div class="column">
          <div>
            <div class="box menu-text">
              <p class="title">Menu</p>
              <div class="field">
                <button :class="['button', tab == 1 ? 'is-primary' : '']" @click="tab = 1">Live feed</button>
              </div>
              <div class="field">
                <button :class="['button', tab == 2 ? 'is-primary' : '']" @click="tab = 2">Charts</button>
              </div>
            </div>
          </div>
        </div>
        <div class="column is-three-quarters">
          <EventsList v-if="tab == 1"/>
          <Charts v-if="tab == 2"/>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import EventsList from './components/EventsList.vue'
import Charts from './components/Charts.vue'

require('./bulma.min.css')

export default {
  name: 'App',

  components: {
    EventsList,
    Charts
  },

  data() {
    return {
      tab: 1
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin-top: 60px;
}
.menu-text {
  text-align: center;
  position: fixed;
}
</style>
