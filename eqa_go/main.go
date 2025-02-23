package main

import (
	"eqa_go/controllers"
	"eqa_go/ext"
	"fmt"
	"github.com/gin-gonic/gin"
)

// dev use
func main() {
	port := 3000
	ext.StartUsgs()
	router := gin.Default()
	router.Use(CORSMiddleware())
	controllers.RegisterMetricRoutes(router)
	router.Run(fmt.Sprintf(":%d", port))
}
