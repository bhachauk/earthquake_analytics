package repo

import (
	"encoding/json"
	"errors"
	"fmt"
	"sync"
	"time"
)

var repo Repo
var repoLock = &sync.Mutex{}

type Repo interface {
	Save(key string, value any) error
	GetAllKeys() ([]string, error)
	Get(key string, retry int) (string, error)
}

func GetRepo() Repo {
	if repo != nil {
		return repo
	}
	repoLock.Lock()
	defer repoLock.Unlock()
	if repo != nil {
		return repo
	}
	repo = NewMockRepo()
	return repo
}

type MockRepo struct {
	data map[string]string
}

func (r *MockRepo) GetAllKeys() ([]string, error) {
	keys := make([]string, 0, len(r.data))
	for k := range r.data {
		keys = append(keys, k)
	}
	return keys, nil
}

func NewMockRepo() *MockRepo {
	return &MockRepo{data: make(map[string]string)}
}

func (r *MockRepo) Save(key string, value any) error {
	jsonData, err := json.Marshal(value)
	if err != nil {
		errorString := fmt.Sprintf("Failed to marshal pairs: %v", err)
		r.data[key] = errorString
		return err
	}
	r.data[key] = string(jsonData)
	return nil
}
func (r *MockRepo) Get(key string, retry int) (string, error) {
	if value, ok := r.data[key]; ok {
		return value, nil
	}
	if retry < 1 {
		return "", errors.New("retry limit reached. try again later")
	}
	time.Sleep(1 * time.Second)
	return r.Get(key, retry-1)
}
