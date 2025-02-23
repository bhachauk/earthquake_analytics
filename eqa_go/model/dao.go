package model

type GraphJSON struct {
	Data   []*GraphData `json:"data"`
	Layout GraphLayout  `json:"layout"`
}

type GraphData struct {
	X      []string     `json:"x"`
	Y      []int        `json:"y"`
	Name   string       `json:"name"`
	Type   string       `json:"type"`
	Mode   string       `json:"mode,omitempty"`
	Marker *GraphMarker `json:"marker,omitempty"`
}

type GraphLayout struct {
	Title        LayoutTitle `json:"title"`
	Xaxis        AxisConfig  `json:"xaxis"`
	Yaxis        AxisConfig  `json:"yaxis"`
	PlotBgColor  string      `json:"plot_bgcolor,omitempty"`
	PaperBgColor string      `json:"paper_bgcolor,omitempty"`
	// Add other layout properties as needed
}

type AxisConfig struct {
	Title Title `json:"title"`
	// Add other axis properties as needed
}

type Title struct {
	Text string `json:"text"`
}

type GraphMarker struct {
	Color string `json:"color"`
	// Add other marker properties as needed
}

type LayoutTitle struct {
	Text string      `json:"text,omitempty"`
	Font *FontConfig `json:"font,omitempty"`
}

type FontConfig struct {
	Size  int    `json:"size,omitempty"`
	Color string `json:"color,omitempty"`
}
