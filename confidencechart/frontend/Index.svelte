<script module lang="ts">
	export { default as BaseConfidenceChart } from "./shared/Label.svelte";
</script>

<script lang="ts">
	import { Gradio } from "@gradio/utils";
	import type { LabelProps, LabelEvents } from "./types";
	import { LineChart as ChartIcon } from "@gradio/icons";
	import { Block, BlockLabel, Empty } from "@gradio/atoms";
	import { StatusTracker } from "@gradio/statustracker";
	import { tweened } from "svelte/motion";
	import { cubicOut } from "svelte/easing";

	let props = $props();
	const gradio = new Gradio<LabelEvents, LabelProps>(props);

	interface Confidence {
		label: string;
		confidence: number;
	}

	let confidences = $derived<Confidence[]>(gradio.props.value?.confidences ?? []);
	let topLabel = $derived<string | undefined>(gradio.props.value?.label ?? undefined);
	let hasData = $derived(confidences.length > 0);

	const COLORS = [
		"#7C3AED",
		"#0EA5E9",
		"#10B981",
		"#F59E0B",
		"#EF4444",
		"#EC4899",
	];

	let animatedWidths = tweened<number[]>([], {
		duration: 600,
		easing: cubicOut,
	});

	$effect(() => {
		const widths = confidences.map((c) => c.confidence * 100);
		if (widths.length === 0) return;
		if ($animatedWidths.length !== widths.length) {
			animatedWidths.set(widths.map(() => 0), { duration: 0 });
		}
		animatedWidths.set(widths);
	});
</script>

<Block
	test_id="confidence-chart"
	visible={gradio.shared.visible}
	elem_id={gradio.shared.elem_id}
	elem_classes={gradio.shared.elem_classes}
	container={gradio.shared.container}
	scale={gradio.shared.scale}
	min_width={gradio.shared.min_width}
	padding={true}
>
	<StatusTracker
		autoscroll={gradio.shared.autoscroll}
		i18n={gradio.i18n}
		{...gradio.shared.loading_status}
		on_clear_status={() => gradio.dispatch("clear_status", gradio.shared.loading_status)}
	/>

	{#if gradio.shared.show_label}
		<BlockLabel
			Icon={ChartIcon}
			label={gradio.shared.label || "Confidence Chart"}
			disable={gradio.shared.container === false}
			float={false}
		/>
	{/if}

	{#if hasData}
		<div class="chart-wrapper">
			{#if topLabel}
				<div class="top-label">
					<span
						class="top-label__pill"
						style="background: {COLORS[0]}22; color: {COLORS[0]}; border-color: {COLORS[0]}44"
					>
						{topLabel}
					</span>
					<span class="top-label__desc">top prediction</span>
				</div>
			{/if}

			<div class="bars" role="list" aria-label="Confidence scores">
				{#each confidences as item, i}
					<div class="bar-row" role="listitem">
						<div class="bar-row__label" title={item.label}>
							{item.label}
						</div>
						<div class="bar-row__track">
							<div
								class="bar-row__fill"
								style="width: {$animatedWidths[i] ?? 0}%; background: {COLORS[i % COLORS.length]};"
							></div>
						</div>
						<div class="bar-row__pct">
							{(item.confidence * 100).toFixed(1)}%
						</div>
					</div>
				{/each}
			</div>
		</div>
	{:else}
		<Empty unpadded_box={true}><ChartIcon /></Empty>
	{/if}
</Block>

<style>
	.chart-wrapper {
		padding: 0.5rem 0.25rem;
	}

	.top-label {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-bottom: 1rem;
	}

	.top-label__pill {
		font-size: 0.8rem;
		font-weight: 600;
		letter-spacing: 0.05em;
		text-transform: uppercase;
		padding: 0.25rem 0.65rem;
		border-radius: 999px;
		border: 1px solid;
	}

	.top-label__desc {
		font-size: 0.75rem;
		color: var(--body-text-color-subdued, #6b7280);
	}

	.bars {
		display: flex;
		flex-direction: column;
		gap: 0.6rem;
	}

	.bar-row {
		display: grid;
		grid-template-columns: 8rem 1fr 3.5rem;
		align-items: center;
		gap: 0.75rem;
	}

	.bar-row__label {
		font-size: 0.85rem;
		font-weight: 500;
		color: var(--body-text-color, #374151);
		text-align: right;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.bar-row__track {
		height: 1.5rem;
		background: var(--border-color-primary, #e5e7eb);
		border-radius: 4px;
		overflow: hidden;
	}

	.bar-row__fill {
		height: 100%;
		border-radius: 4px;
		min-width: 2px;
	}

	.bar-row__pct {
		font-size: 0.8rem;
		font-weight: 600;
		color: var(--body-text-color, #374151);
		font-variant-numeric: tabular-nums;
	}
</style>