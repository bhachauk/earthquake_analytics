package workers

import (
	"eqa_go/model"
	"fmt"
	"log"
	"sync"
)

type Worker interface {
	Name() string
	startWork(*model.FeatureCollection, *sync.WaitGroup) error
}

func StartAllWorkers(data *model.FeatureCollection) error {
	workers := []Worker{
		NewTopAreasWorker(),
		NewTopNToday(10),
		NewLastNDaysDistribution(30),
	}
	wg := &sync.WaitGroup{}
	errCount := 0
	for _, worker := range workers {
		wg.Add(1)
		go func() {
			err := worker.startWork(data, wg)
			if err != nil {
				log.Fatalf("Error starting worker: %v", err)
				errCount++
			}
		}()
	}
	wg.Wait()
	if errCount > 0 {
		return fmt.Errorf("%d workers failed to start", errCount)
	}
	return nil
}
