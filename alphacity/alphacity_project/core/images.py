"""Live photos hosted by Unsplash (free licence). Swap any ID/URL to change a picture."""
def u(photo_id, w=1400):
    return f"https://images.unsplash.com/photo-{photo_id}?auto=format&fit=crop&q=70&w={w}"

IMAGES = {
    "hero": u("1758707844957-559cc02df8ef", 1800),
    "bins1": u("1596571026162-ba38f30d222e"),
    "bins2": u("1761479141212-e90931a0f523"),
    "bins3": u("1532996122724-e3c354a0b15b"),
    "bins4": u("1528190336454-13cd56b45b5a"),
    "street": u("1737311973956-307113b3a86b"),
    "pile": u("1605600659908-0ef719419d41"),
}
IMAGES.update({
    "banner": u("1737311973956-307113b3a86b", 900),
    "t1": u("1596571026162-ba38f30d222e", 400),
    "t2": u("1761479141212-e90931a0f523", 400),
    "t3": u("1532996122724-e3c354a0b15b", 400),
})
