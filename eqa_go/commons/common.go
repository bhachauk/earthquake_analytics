package commons

import (
	"fmt"
	"sort"
	"strconv"
	"strings"
)

const (
	TopNToday     = "top_n_today"
	TopAreas      = "top_areas"
	LastNDaysDist = "last_n_days_dist"

	AppBgColor = "#fcfcfc"
)

var Metrics = []string{
	TopNToday,
	TopAreas,
}

type Pair struct {
	Key   string
	Value int
}

type LatLongPair struct {
	Lat, Long, Step float64
	Key             string
}

func NewLatLongPair(long, lat, step float64) *LatLongPair {
	return &LatLongPair{
		Lat:  lat,
		Long: long,
		Step: step,
		Key:  fmt.Sprintf("%d,%d", int(lat/step), int(long/step)),
	}
}

func NewLatLongPairFromKey(key string, step float64) *LatLongPair {
	keyParse := strings.Split(key, ",")
	long, _ := strconv.ParseFloat(keyParse[0], 64)
	lat, _ := strconv.ParseFloat(keyParse[1], 64)
	return &LatLongPair{
		Key:  key,
		Lat:  lat * step,
		Long: long * step,
		Step: step,
	}
}

func (pair *LatLongPair) GetRectLines() ([]float64, []float64) {
	lat, lat1, long, long1 := pair.Lat, pair.Lat+pair.Step, pair.Long, pair.Long+pair.Step
	return []float64{lat, lat1, lat1, lat, lat}, []float64{long, long, long1, long1, long}
}

type Counter struct {
	counts map[string]int
}

func NewCounter() *Counter {
	return &Counter{counts: make(map[string]int)}
}

func (c *Counter) Add(item string) {
	c.counts[item]++
}

func (c *Counter) SortedCounts() []Pair {

	var pairs []Pair
	for k, v := range c.counts {
		pairs = append(pairs, Pair{k, v})
	}

	sort.Slice(pairs, func(i, j int) bool {
		return pairs[i].Value > pairs[j].Value // Descending order
	})

	return pairs
}
