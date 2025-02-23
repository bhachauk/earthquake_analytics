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

func (worker *TopAreasWorker) startWork(data *model.FeatureCollection, wg *sync.WaitGroup) error {
	defer wg.Done()
	counter := commons.NewCounter()
	for _, feature := range data.Features {
		long, lat := feature.Geometry.Coordinates[0].(float64), feature.Geometry.Coordinates[1].(float64)
		key := fmt.Sprintf("%v,%v", int(long/worker.div), int(lat/worker.div))
		counter.Add(key)
	}
	pairs := counter.SortedCounts()
	repo.GetRepo().Save(commons.TopAreas, pairs)
	log.Println("[INFO]: metric completed: ", commons.TopAreas)
	return nil
}
