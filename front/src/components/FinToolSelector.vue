<template>
    <select v-model="selected" @change="onChange($event)">
        <option v-for="option in options" :value="option.value" :key="option.value">
            {{ option.text }}
        </option>
    </select>
</template>

<script>
export default {
    data() {
        return {
            selected: '',
            options: []
        }
    },
    mounted() {
        fetch("http://localhost:8000/fin_tools")
            .then(response => response.json())
            .then(data => this.setData(data))
    },
    methods: {
        onChange(event) {
            this.$emit('selected-tool-changed', event.target.value)
        },
        setData(data) {
            this.options = data;
            this.selected = data[0].value;
        }
    },
    emits: ['selected-tool-changed']
}
</script>