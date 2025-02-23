package commons

import (
	"fmt"
	"testing"
)

func TestCounter(t *testing.T) {
	vals := []string{"apple", "banana", "cherry", "cherry", "banana", "cherry"}
	t.Run("counter test", func(t *testing.T) {
		counter := NewCounter()
		for _, val := range vals {
			counter.Add(val)
		}
		for _, val := range vals {
			fmt.Println(val)
		}

	})
}
