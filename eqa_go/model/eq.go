package model

import (
	"time"
)

type FeatureCollection struct {
	Type     string     `json:"type"`
	Metadata *Metadata  `json:"metadata"`
	Features []*Feature `json:"features"`
}

type Metadata struct {
	Generated int64  `json:"generated"`
	URL       string `json:"url"`
	Title     string `json:"title"`
	Status    int    `json:"status"`
	API       string `json:"api"`
	Count     int    `json:"count"`
}

type Feature struct {
	Type       string      `json:"type"`
	Properties *Properties `json:"properties"`
	Geometry   *Geometry   `json:"geometry"`
	ID         string      `json:"id"`
}

type Properties struct {
	Mag     float64  `json:"mag"`
	Place   string   `json:"place"`
	Time    int64    `json:"time"`
	Updated int64    `json:"updated"`
	Tz      *int     `json:"tz"` // Use a pointer for nullable values
	URL     string   `json:"url"`
	Detail  string   `json:"detail"`
	Felt    *int     `json:"felt"`  // Pointer for nullable
	Cdi     *float64 `json:"cdi"`   // Pointer for nullable
	Mmi     *float64 `json:"mmi"`   // Pointer for nullable
	Alert   *string  `json:"alert"` // Pointer for nullable
	Status  string   `json:"status"`
	Tsunami int      `json:"tsunami"`
	Sig     int      `json:"sig"`
	Net     string   `json:"net"`
	Code    string   `json:"code"`
	IDs     string   `json:"ids"`
	Sources string   `json:"sources"`
	Types   string   `json:"types"`
	Nst     *int     `json:"nst"`  // Pointer for nullable
	Dmin    *float64 `json:"dmin"` // Pointer for nullable
	RMS     float64  `json:"rms"`
	Gap     *float64 `json:"gap"` // Pointer for nullable
	MagType string   `json:"magType"`
	Type    string   `json:"type"`
	Title   string   `json:"title"`
}

type Geometry struct {
	Type        string        `json:"type"`
	Coordinates []interface{} `json:"coordinates"` // Or [3]float64 if always 3 numbers
}

// Helper function to convert Unix milliseconds to time.Time
func (p *Properties) TimeAsTime() time.Time {
	return time.Unix(p.Time/1000, (p.Time%1000)*1e6)
}

func (p *Properties) UpdatedAsTime() time.Time {
	return time.Unix(p.Updated/1000, (p.Updated%1000)*1e6)
}
