import type { SelectData, CustomButton } from "@gradio/utils";
import type { LoadingStatus } from "@gradio/statustracker";

export interface LabelProps {
	value: {
		label?: string;
		confidences?: { label: string; confidence: number }[];
	};
	color: string | undefined;
	_selectable: boolean;
	show_heading: boolean;
	buttons: (string | CustomButton)[] | null;
}

export interface LabelEvents {
	change: never;
	select: SelectData;
	clear_status: LoadingStatus;
	custom_button_click: { id: number };
}