# Hangar coloring preview does not refresh

The user reports that selecting a color leaves the frame's live preview
unchanged. Leaving HANGAR and entering it again displays the selected color.
The supplied capture shows a green selection with a blue frame. This suggests
that the selection is accepted but the existing model preview is not refreshed;
it does not establish whether the original game or Vita3K causes the problem.

Workaround: after choosing colors, leave HANGAR and enter it again.

On 2026-10-25, a read-only audit compared the original archive, local 0.1.16
candidate and the installed English archive. All 312 selected members were
byte-identical to the original: every `data/_chr` model member and all paths
matching hangar/color/custom/shader/material or `.gxp`. This includes
`MENU_HANGAR.bsw`, `custom.bnd`, the coloring/paint animation assets and
`custom_cursor.btx`. The installed executable also matches the original.
The [audit record](../work/ui/coloring-preview-issue.json) contains identities
and the local screenshot reference.

This makes a direct change to coloring assets or executable logic an unlikely
explanation. It does not rule out indirect effects of shared text/font changes.
The [upstream compatibility report](https://github.com/Vita3K/compatibility/issues/655)
does not document this exact symptom; it is not confirmation of its cause.

Status: cause unconfirmed. A controlled comparison of the same coloring action
in the original Japanese game under the same Vita3K settings would distinguish
a translation regression. A physical Vita comparison is needed before calling
it an original-game bug. No game files, settings, saves or licenses were changed.
Version remains 0.1.16; no new build, release or source push.
