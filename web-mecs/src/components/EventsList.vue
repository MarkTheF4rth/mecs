<template>
<div>
  <div class="box" v-for="(event, index) in events" :key="index">
    <p class="time">{{ event.time }}</p>
    <table class="table table-striped">
      <tbody>
        <tr>
          <th>Event</th>
          <td>{{ event.event }}</td>
        </tr>
        <tr>
          <th>Node</th>
          <td>{{ event.node }}</td>
        </tr>
        <tr>
          <th>Level</th>
          <td>{{ event.level }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'EventsList',

  props: {
  },

  data() {
    return {
      events: [],
      timedRequests: {},
    }
  },

  mounted() {
    this.getData();
    this.timedRequests = setInterval(this.getData, 2000);
  },

  beforeDestroy() {
    clearInterval(this.timedRequests);
  },

  methods: {
    getData() {
      axios.get(process.env.VUE_APP_EVENTS_ENDPOINT).then(response => {
        this.events = response.data.reverse();

        for (let i = 0; i < this.events.length; i++) {
          this.events[i].time = this.formatTime(this.events[i]);
        }
      });
    },
    
    formatTime(event) {
      let date = new Date(event.time * 1000); //UNIX timestamp is in seconds, we need it in milliseconds

      let months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
      let year = date.getFullYear();
      let month = months[date.getMonth()];
      let day = date.getDate();
      let hour = (date.getHours() < 10 ? '0' : '') + date.getHours();
      let minute = (date.getMinutes() < 10 ? '0' : '') + date.getMinutes();
      let second = (date.getSeconds() < 10 ? '0' : '') + date.getSeconds();

      return day + ' ' + month + ' ' + year + ' ' + hour + ':' + minute + ':' + second;
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
.time {
  text-align: right;
}
</style>
