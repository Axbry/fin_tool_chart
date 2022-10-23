<template>
  <div>
    <FinToolSelector @selected-tool-changed="selectedToolChanged" />
    <TimeFrameSelector @selected-tool-changed="timeFrameChanged" />
    <button @click="onBuildChartClick()">Build Chart</button>
    <Line :chart-data="this.chartData" :chart-options="chartOptions" />
  </div>
</template>


<script>
import { Line } from "vue-chartjs";
import FinToolSelector from "./FinToolSelector.vue";
import TimeFrameSelector from "./TimeFrameSelector.vue"

import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  LineElement,
  PointElement,
} from "chart.js";

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  PointElement,
  BarElement,
  CategoryScale,
  LinearScale,
  LineElement
);
export default {
  name: "LineChart",
  components: {
    Line,
    FinToolSelector,
    TimeFrameSelector
  },
  props: {},
  sse: {
    cleanup: true,
  },
  data: () => ({
    chartData: {},
    chartOptions: {},
    sseClient: null,
    timeFrame: "SEC",
    ticker: 'ticker_00'
  }),
  mounted() {
    this.chartOptions = {
      responsive: true,
      maintainAspectRatio: false,
    };

  },
  methods: {
    selectedToolChanged(ticker) {
      this.ticker = ticker
    },
    onBuildChartClick() {
      fetch("http://localhost:8000/price/" + this.ticker + "/" + this.timeFrame)
        .then((response) => response.json())
        .then((data) => this.processPriceData(data));
    },
    timeFrameChanged(timeFrame) {
        this.timeFrame = timeFrame;
    },
    handleEvents(message) {
      this.chartData.labels.push(message.label);
      this.chartData.datasets[0].data.push(message.data);

    },
    handleOff(message) {
      console.log("my error" + message);
    },
    processPriceData(data) {
      this.chartData = data.chart_data;

      if (this.sseClient)
        this.sseClient.disconnect();

      var extra = data.extra_data
      this.sseClient = this.$sse.create({
        url: 'http://localhost:8000/stream_data/' + extra.ticker + "/" + this.timeFrame + "/" + extra.last_time_stamp, 
        format: 'json'});
     
      this.sseClient.connect()
        .then(sseClient => {
            console.log("start connect")
            sseClient.on('message', this.handleEvents);
            sseClient.off('message', this.handleOff)
          })
          .catch(err => {
            console.log("err connect" + err)
          });
    }
  },
};
</script>
