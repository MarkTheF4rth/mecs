<template>
<div id='data-charts'>
    <div class='box has-text-centered'>
        <h2>
            Severity of recent events
        </h2>
        <GChart
            type="ColumnChart"
            :data="columnChartData"
            :options="columnChartOptions"
        />
    </div>
    <div class='box has-text-centered'>
        <h2>
            Distribution of severities in recent events
        </h2>
        <GChart
            :settings="{ packages: ['corechart'] }"
            type="PieChart"
            :data="pieChartData"
            :options="pieChartOptions"
            style="display: inline-block; margin: 0 auto;"
        />
    </div>
    <div class="box has-text-centered">
        <h2>
            Overall system state based on severity of recent events
        </h2>
        <GChart
            :settings="{ packages: ['gauge'] }"
            type="Gauge"
            :data="gaugeChartData"
            :options="gaugeChartOptions"
            style="display: inline-block; margin: 0 auto;"
        />
      <h3>
        <br>
        '0' - Everything is working perfectly
        <br>
        '1' - Everything is in a fatal state
      </h3>
    </div>
  </div>
</template>

<script>
import { GChart } from 'vue-google-charts';
import axios from 'axios'

export default {
  name: 'Charts',

  components: {
      GChart
  },

  props: {
  },

  data() {
    return {
      timedRequests: {},

      // Column Chart
      columnChartData: [],
      columnChartOptions: {
        bar: {groupWidth: '75%'},
        height: 400,
        hAxis: {
          textPosition: 'none'
        }
      },

      // Pie Chart 
      pieChartData: [],
      pieChartOptions: {
          is3D: true,
          height: 400,
          width: 600
      },

      // Gauge Chart
      gaugeChartData: [],
      gaugeChartOptions: {
        width: 260, 
        height: 260,
        redFrom: 0.85, 
        redTo: 1,
        yellowFrom: 0.65, 
        yellowTo: 0.85,
        greenFrom: 0,
        greenTo: 0.65,
        minorTicks: 5,
        max: 1,
        min: 0,
      },
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
            let data = response.data;
            if (data.length > 0) {
                this.columnChartData = this.prepareColumnChartData(data);
                this.pieChartData = this.preparePieChartData(data);
                this.gaugeChartData = this.prepareGaugeChartData(data); 
            }
        });
      },

    severityTranslation: function(severity) {
        var dict = {
            "Normal": 1, 
            "Minor": 2, 
            "Warning": 3, 
            "Major": 4, 
            "Critical": 5, 
            "Fatal": 6
        }; 
        return dict[severity];
    },

    prepareColumnChartData: function(data) {
        var newData = [];
        newData.push(["Index", "Severity"]);

        for(let i = 0; i < data.length; i++){
            newData.push([i + 1, this.severityTranslation(data[i]["level"])]);
        } 
        return newData;
    },

    preparePieChartData: function(data) {
        var severities = {
            'Normal': 0,
            'Minor': 0,
            'Warning': 0,
            'Major': 0,
            'Critical': 0,
            'Fatal': 0,
        };

        for(let i = 0; i < data.length; i++) {
            severities[data[i]["level"]]++;
        }

        var newData = [['Severity', 'Number of occurances']]
        for(let key in severities) {
            newData.push([key, severities[key]]);
        }

        return newData;
    },

    prepareGaugeChartData: function(data) {
        var levels = [];
        
        for(let i = 0; i < data.length; i++) {
            if (data[i]["level"]) {
                levels.push(this.severityTranslation(data[i]["level"]));
            }
        }

        var min = Math.min(...levels);
        var max = Math.max(...levels);
        if (min == max) {
            var newData = [['Label', 'Value']];
            newData.push(['Severity', min]);
            return newData;
        }
        var levels_scaled = [];
        for(let j = 0; j < levels.length; j++) {
            // min-max normalization [0, 1]
            var scaled = (levels[j] - min) / (max - min)
            levels_scaled.push(scaled)
        }

        var avg = 0
        for(var k = 0; k < levels_scaled.length; k++) {
            avg += levels_scaled[k];
        }
        avg = avg / levels_scaled.length;

        newData = [['Label', 'Value']];
        newData.push(['Severity', avg]);
        return newData;
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
