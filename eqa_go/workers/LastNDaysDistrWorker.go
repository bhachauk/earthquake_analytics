package workers

import (
	"eqa_go/commons"
	"eqa_go/model"
	"eqa_go/repo"
	"fmt"
	"log"
	"sync"
	"time"
)

type NDaysFeature struct {
	name     string
	start    int64
	end      int64
	magCount map[int]int
}

func NewNDaysFeature(startDate time.Time, days int, name string) *NDaysFeature {
	statTime := time.Date(startDate.Year(), startDate.Month(), startDate.Day(), 0, 0, 0, 0, time.UTC)
	endDate := statTime.AddDate(0, 0, days)
	return &NDaysFeature{
		start:    statTime.Unix(),
		end:      endDate.Unix(),
		magCount: make(map[int]int),
		name:     name,
	}
}

func (n *NDaysFeature) AddFeature(feature *model.Feature) {
	inputTime := feature.Properties.Time / 1000
	if n.start <= inputTime && n.end > inputTime {
		mag := int(feature.Properties.Mag)
		if feature.Properties.Mag > 7 {
			mag = 7
		}
		n.magCount[mag]++
	}
}

type LastNDaysDist struct {
	lastN int
}

func NewLastNDaysDistribution(last int) *LastNDaysDist {
	return &LastNDaysDist{lastN: last}
}

func (t *LastNDaysDist) Name() string {
	return "last_n_dist"
}

func getLastNDistGraph(trace1 *model.GraphData, trace2 *model.GraphData) (any, error) {
	return &model.GraphJSON{
		Data: []*model.GraphData{
			trace1,
			trace2,
		},
		Layout: model.GraphLayout{
			Title: model.LayoutTitle{
				Text: "Last 30 days vs Previous",
				Font: &model.FontConfig{
					Size:  10,
					Color: "red",
				},
			},
			Xaxis: model.AxisConfig{
				Title: model.Title{Text: "Magnitude"},
			},
			Yaxis: model.AxisConfig{
				Title: model.Title{Text: "Count"},
			},
			PaperBgColor: commons.AppBgColor,
			PlotBgColor:  commons.AppBgColor,
		},
	}, nil
}

func getLastNDistTrace(nDays *NDaysFeature) *model.GraphData {
	x := make([]string, 0)
	y := make([]int, 0)
	for mag := 2; mag < 8; mag++ {
		x = append(x, fmt.Sprintf("%d", mag))
		y = append(y, nDays.magCount[mag])
	}
	return &model.GraphData{
		X:    x,
		Y:    y,
		Name: nDays.name,
		Type: "bar",
	}
}

func (t *LastNDaysDist) startWork(data *model.FeatureCollection, wg *sync.WaitGroup) error {
	defer wg.Done()
	now := time.Now()
	before := NewNDaysFeature(now.AddDate(0, 0, -1*t.lastN), t.lastN, "Last 30 Days")
	previous := NewNDaysFeature(now.AddDate(0, 0, -2*t.lastN), t.lastN, "Previous 30 Days")
	for _, feature := range data.Features {
		before.AddFeature(feature)
		previous.AddFeature(feature)
	}
	beforeData := getLastNDistTrace(before)
	previousData := getLastNDistTrace(previous)
	graphData, err := getLastNDistGraph(beforeData, previousData)
	if err != nil {
		return err
	}
	repo.GetRepo().Save(commons.LastNDaysDist, graphData)
	log.Println("[INFO]: metric completed: ", commons.LastNDaysDist)
	return nil
}
