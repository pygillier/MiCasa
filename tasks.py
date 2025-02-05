from invoke import task, call


@task
def build_css(c, component="manage"):
    c.run(f"npx tailwindcss build -i static/src/{component}.css -o static/css/{component}.css --watch")


@task(post=[build_css])
def build_manage(c):
    print("Starting tailwindcss build for manage component")


@task(post=[call(build_css, component="front")])
def build_front(c):
    print("Starting tailwindcss build for front component")


@task
def build_container(c):
    print("Building container")
    c.run("docker build -t micasa:local .")


@task
def run_container(c):
    print("Running container")
    c.run("docker run --rm -e SECRET_KEY=local -p 8080:8000 micasa:local")
