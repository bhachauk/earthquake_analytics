package workers

import (
	"eqa_go/commons"
	"eqa_go/model"
	"eqa_go/repo"
	"fmt"
	"log"
	"sync"
)

type TopAreasWorker struct {
	div float64
}

func NewTopAreasWorker() *TopAreasWorker {
	return &TopAreasWorker{div: 10}
}

func (w *TopAreasWorker) Name() string {
	return "top_areas"
}

func (w *TopAreasWorker) getTopAreaGraphData(pairs []commons.Pair) (*model.ScatterGeoJSON, error) {
	var area_data []model.ScatterGeo
	for _, pair := range pairs {
		latLong := commons.NewLatLongPairFromKey(pair.Key, w.div)
		rectLon, rectLat := latLong.GetRectLines()
		area_data = append(area_data, model.ScatterGeo{
			Type: "scattergeo",
			Mode: "lines",
			Name: fmt.Sprintf("%d", pair.Value),
			Marker: &model.GeoMarker{
				Color: "red",
			},
			Lon: rectLon,
			Lat: rectLat,
			Line: model.Line{
				Color: "blue",
			},
		})
	}
	return &model.ScatterGeoJSON{
		Data: area_data,
		Layout: model.GeoLayout{
			Title: model.LayoutTitle{
				Text: "Top affected areas with more earthquakes",
				Font: &model.FontConfig{
					Size:  10,
					Color: "red",
				},
			},
			Geo: model.GeoConfig{
				Lonaxis: &model.AxisConfig{
					Dtick:    10,
					Showgrid: true,
				},
				Lataxis: &model.AxisConfig{
					Dtick:    10,
					Showgrid: true,
				},
			},
			PaperBgColor: commons.AppBgColor,
			PlotBgColor:  commons.AppBgColor,
			ShowLegend:   false,
		},
	}, nil
}

func (worker *TopAreasWorker) startWork(data *model.FeatureCollection, wg *sync.WaitGroup) error {
	defer wg.Done()
	counter := commons.NewCounter()
	for _, feature := range data.Features {
		long, lat := feature.Geometry.Coordinates[0].(float64), feature.Geometry.Coordinates[1].(float64)
		latLongPair := commons.NewLatLongPair(long, lat, worker.div)
		counter.Add(latLongPair.Key)
	}
	pairs := counter.SortedCounts()
	// Show only top 10 pairs
	top_pairs := pairs[:10]
	jsonData, err := worker.getTopAreaGraphData(top_pairs)
	if err != nil {
		return err
	}
	repo.GetRepo().Save(commons.TopAreas, jsonData)
	log.Println("[INFO]: metric completed: ", commons.TopAreas)
	return nil
}
