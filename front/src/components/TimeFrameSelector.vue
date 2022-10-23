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
            selected: 'SEC',
            options: [
                {"value": "SEC", "text": "1 секунда"},
                {"value": "10SEC", "text": "10 секунд"},
                {"value": "MIN", "text": "1 минута"},
                {"value": "10MIN", "text": "10 минут"},
                {"value": "HOUR", "text": "1 час"},
            ]
        }
    },
    methods: {
        onChange(event) {
            this.$emit('selected-tool-changed', event.target.value)
        }
    },
    emits: ['selected-tool-changed']
}
</script>