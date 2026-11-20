from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from hiking import __version__


@require_GET
def health(request):
    """Report the running version and whether the database is usable."""
    try:
        executor = MigrationExecutor(connection)
        pending = executor.migration_plan(executor.loader.graph.leaf_nodes())
        database = "ok"
    except Exception:  # any database failure makes the service unhealthy
        pending = []
        database = "error"

    healthy = database == "ok"
    return JsonResponse(
        {
            "status": "ok" if healthy else "error",
            "version": __version__,
            "database": database,
            "pending_migrations": len(pending),
        },
        status=200 if healthy else 503,
    )


def not_found(request, exception=None):
    return JsonResponse({"error": "not_found"}, status=404)


def server_error(request):
    return JsonResponse({"error": "internal_error"}, status=500)
