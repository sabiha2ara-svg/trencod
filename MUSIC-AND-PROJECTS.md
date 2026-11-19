# Trencod 0.12.0 — My projects and music

## Apply the update
1. Download your current project backup first (Profile or My projects). Keep the existing Neon DATABASE_URL in Render.
2. Extract this ZIP. Upload/replace its **trencod-app** folder at the existing GitHub repository root. Do not create trencod-app/trencod-app.
3. Commit the changed files. In Render, deploy the latest commit if auto-deploy does not start.
4. Wait for Deploy succeeded. Open `/healthz`: version must be **0.12.0**, storage **postgres** for Neon.
5. Refresh the website with Ctrl+Shift+R. If the installed app is still old, open the website in a browser and refresh there too.

The ZIP does not update the live site by itself. No new environment variable or AI key is required for music. Do not delete/reset your database.

## Save and find artwork
- Design → Pixel art & animation → draw → enter a name → **Save to My projects**.
- One frame is listed as Pixel art. Two or more frames are listed as Animation.
- Design → Vector art → draw → **Save to My projects**.
- **My projects** now includes games, pixel art, animations and vector art; use the Show filter and search. Click **Open & edit** to reopen. Artwork cards show the first frame or vector preview.
- Existing saved art appears automatically. Team files you still have access to appear with their Studio name. Files sold exclusively appear for the new owner, not the old seller.
- The small Pixel art drawer inside Code also has **Save to My projects**, separate from Insert into game.
- Download PNG exports an image to your computer; it is not an account save. Use Save to My projects to keep editable frames/shapes in your account.
- Save requires sign-in. A failed save keeps your editor open and shows an error. If a file was never saved or the old database was already lost, this update cannot recover it.

## Add music
- Animation: **Add / change music** in Animation preview.
- Code game: **Music** in the editor toolbar.
- Visual game: **Music** beside Play preview.
- Upload your own MP3/Ogg/WAV or select a previously uploaded clip. Set volume and Loop, press **Use this music**, then **Save** in the editor.
- Animation preview: Play animation starts its music; Pause pauses it. The exported animation's audio Play/Pause also starts/pauses its frames.
- Game preview and published/exported games show audio Play/Pause controls. Browsers require a player click; sound does not autoplay.
- Remove music detaches it from that creation. The reusable clip remains saved.

Limits: 300,000 bytes per clip, 20 uploaded clips per account. These are short loops/sound clips, not long songs. A compressed MP3 is usually smaller than WAV. Use music you own or have permission to share.

Uploaded audio is saved in the database (Neon when configured), not on Render's temporary disk. Clips are immutable so an old published game keeps its sound. Anyone with a clip's link can play it. Artwork and game export files reference the hosted clip: music needs internet access and your Trencod service to remain available. PNG sprite sheets cannot contain sound. Account backups now also include your uploaded clips; editable art/scene JSON stores the clip reference.

The AI connection is unchanged by this update.
