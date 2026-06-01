from locust import HttpUser, task, between
import random
import string

def nombre_aleatorio():
    return "user_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))


class UsuarioPredictor(HttpUser):
    wait_time = between(1, 3)
    token = None
    sala_id = None
    sala_codigo = None

    def on_start(self):
        """Registrar e iniciar sesión al arrancar cada usuario simulado."""
        self.nombre = nombre_aleatorio()
        self.password = "test1234"

        # Registro
        r = self.client.post("/registro", json={"nombre": self.nombre, "password": self.password})
        if r.status_code == 200:
            self.token = r.json().get("access_token")
        else:
            # Si ya existe, hacer login
            r = self.client.post("/login", json={"nombre": self.nombre, "password": self.password})
            if r.status_code == 200:
                self.token = r.json().get("access_token")

        if not self.token:
            return

        # Crear una sala propia
        r = self.client.post(
            f"/salas?token={self.token}",
            json={"nombre": f"Sala de {self.nombre}"}
        )
        if r.status_code == 200:
            data = r.json()
            self.sala_id = data["sala_id"]
            self.sala_codigo = data["codigo"]

            # Crear un partido de prueba en la sala
            r2 = self.client.post(
                f"/salas/{self.sala_id}/partidos?token={self.token}",
                json={
                    "equipo_local": "Argentina",
                    "equipo_visitante": "Brasil",
                    "fecha_partido": "2026-07-01T20:00:00"
                }
            )
            if r2.status_code == 200:
                self.partido_id = r2.json().get("partido_id")
            else:
                self.partido_id = None
        else:
            self.sala_id = None
            self.partido_id = None

    @task(3)
    def ver_ranking(self):
        if self.sala_id:
            self.client.get(f"/salas/{self.sala_id}/ranking")

    @task(3)
    def ver_partidos(self):
        if self.sala_id:
            self.client.get(f"/salas/{self.sala_id}/partidos")

    @task(2)
    def hacer_prediccion(self):
        if not self.token or not getattr(self, "partido_id", None):
            return
        self.client.post(
            f"/partidos/{self.partido_id}/predicciones?token={self.token}",
            json={
                "goles_local": random.randint(0, 4),
                "goles_visitante": random.randint(0, 4)
            }
        )

    @task(1)
    def login_task(self):
        """Simula logins concurrentes."""
        self.client.post(
            "/login",
            json={"nombre": self.nombre, "password": self.password}
        )

    @task(1)
    def registrar_resultado(self):
        """Solo el creador puede registrar resultado — simula esa acción."""
        if not self.token or not getattr(self, "partido_id", None):
            return
        self.client.post(
            f"/partidos/{self.partido_id}/resultado?token={self.token}",
            json={
                "goles_local": random.randint(0, 3),
                "goles_visitante": random.randint(0, 3)
            }
        )