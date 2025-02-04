from invoke import task


@task
def build_css(c, component="manage"):
    c.run(f"npx tailwindcss build -i static/src/{component}.css -o static/css/{component}.css --watch")


@task(post=[build_css])
def build_manage_css(c):
    print("Starting tailwindcss build for manage component")
