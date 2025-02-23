package workers

import (
	"eqa_go/commons"
	"eqa_go/model"
	"eqa_go/repo"
	"fmt"
	"log"
	"sort"
	"sync"
	"time"
)

type TopNToday struct {
	topN int
}

func NewTopNToday(topN int) *TopNToday {
	return &TopNToday{topN: topN}
}

func (t *TopNToday) Name() string {
	return "top_n_today"
}

func getTopNGraph(features []*model.Feature) (any, error) {
	x := make([]float64, 0)
	y := make([]float64, 0)
	text := make([]string, 0)
	size := make([]int, 0)
	for _, feature := range features {
		long, lat := feature.Geometry.Coordinates[0].(float64), feature.Geometry.Coordinates[1].(float64)
		x = append(x, lat)
		y = append(y, long)
		text = append(text, fmt.Sprintf("%.2f %s <br> %s", feature.Properties.Mag, feature.Properties.Place,
			time.Unix(int64(int(feature.Properties.Time/1000)), 0).Format(time.RFC3339)))
		size = append(size, int(feature.Properties.Mag)*4)
	}
	return &model.ScatterGeoJSON{
		Data: []model.ScatterGeo{
			{
				Type: "scattergeo",
				Mode: "markers",
				Marker: &model.GeoMarker{
					Size:  size,
					Color: "red",
				},
				Lat:  x,
				Lon:  y,
				Text: text,
			},
		},
		Layout: model.GeoLayout{
			Title: model.LayoutTitle{
				Text: "Top 10 Earthquakes Today",
				Font: &model.FontConfig{
					Size:  10,
					Color: "red",
				},
			},
			Geo: model.GeoConfig{
				Projection: model.GeoProjection{
					Type: "natural earth",
				},
			},
			PaperBgColor: commons.AppBgColor,
			PlotBgColor:  commons.AppBgColor,
		},
	}, nil
}

func (t *TopNToday) startWork(data *model.FeatureCollection, wg *sync.WaitGroup) error {
	defer wg.Done()
	var todayEqs []*model.Feature
	now := time.Now()
	startOfDayUTC := time.Date(now.Year(), now.Month(), now.Day(), 0, 0, 0, 0, time.UTC)
	for _, feature := range data.Features {
		if (feature.Properties.Time / 1000) < startOfDayUTC.Unix() {
			break
		}
		todayEqs = append(todayEqs, feature)
	}
	sort.Slice(todayEqs, func(i, j int) bool {
		return todayEqs[i].Properties.Mag > todayEqs[j].Properties.Mag
	})
	if len(todayEqs) > t.topN {
		todayEqs = todayEqs[:t.topN]
	}
	graphData, err := getTopNGraph(todayEqs)
	if err != nil {
		return err
	}
	repo.GetRepo().Save(commons.TopNToday, graphData)
	log.Println("[INFO]: metric completed: ", commons.TopNToday, t.topN)
	return nil
}
