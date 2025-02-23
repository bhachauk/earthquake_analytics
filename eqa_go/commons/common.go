package commons

import (
	"sort"
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
