from .learners import router as learners_router
from .goals import router as goals_router
from .skills import router as skills_router
from .recommendations import router as recommendations_router
from .roadmap import router as roadmap_router
from .assessments import router as assessments_router
from .progress import router as progress_router
from .coach import router as coach_router
from .resources import router as resources_router

routers = [
    (learners_router, "/api/learners", ["learners"]),
    (goals_router, "/api/goals", ["goals"]),
    (skills_router, "/api/learners/{learner_id}/skills", ["skills"]),
    (recommendations_router, "/api/learners/{learner_id}/recommendations", ["recommendations"]),
    (roadmap_router, "/api/learners/{learner_id}/roadmap", ["roadmap"]),
    (assessments_router, "/api/assessments", ["assessments"]),
    (progress_router, "/api/learners/{learner_id}/progress", ["progress"]),
    (coach_router, "/api/learners/{learner_id}/coach", ["coach"]),
    (resources_router, "/api/resources", ["resources"])
]
