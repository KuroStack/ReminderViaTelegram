<?php

namespace App\Telegram\Handlers;

use App\Models\Recipe;
use App\Models\RecipeCategory;
use App\Telegram\Keyboards;
use Telegram\Bot\Laravel\Facades\Telegram;
use Telegram\Bot\Objects\Update;

class RecipeHandler
{
    public function handleCategories(Update $update): void
    {
        $cbq    = $update->getCallbackQuery();
        $chatId = $cbq->getMessage()->getChat()->getId();
        $msgId  = $cbq->getMessage()->getMessageId();

        Telegram::answerCallbackQuery(['callback_query_id' => $cbq->getId()]);

        $categories = RecipeCategory::all();

        if ($categories->isEmpty()) {
            Telegram::editMessageText([
                'chat_id'      => $chatId,
                'message_id'   => $msgId,
                'text'         => 'No recipe categories yet.',
                'reply_markup' => json_encode(Keyboards::backButton()),
            ]);
            return;
        }

        $buttons = $categories->map(fn ($c) => [
            ['text' => $c->name, 'callback_data' => "recipe:list:{$c->id}"],
        ])->toArray();
        $buttons[] = [['text' => '« Back', 'callback_data' => 'main:menu']];

        Telegram::editMessageText([
            'chat_id'      => $chatId,
            'message_id'   => $msgId,
            'text'         => '*Recipe Categories*',
            'parse_mode'   => 'Markdown',
            'reply_markup' => json_encode(['inline_keyboard' => $buttons]),
        ]);
    }

    public function handleList(Update $update, int $catId): void
    {
        $cbq    = $update->getCallbackQuery();
        $chatId = $cbq->getMessage()->getChat()->getId();
        $msgId  = $cbq->getMessage()->getMessageId();

        Telegram::answerCallbackQuery(['callback_query_id' => $cbq->getId()]);

        $category = RecipeCategory::find($catId);
        $recipes  = Recipe::where('category_id', $catId)->get();

        if ($recipes->isEmpty()) {
            Telegram::editMessageText([
                'chat_id'      => $chatId,
                'message_id'   => $msgId,
                'text'         => 'No recipes in this category.',
                'reply_markup' => json_encode(Keyboards::backButton('recipe:categories', '« Categories')),
            ]);
            return;
        }

        $buttons = $recipes->map(fn ($r) => [
            ['text' => $r->name, 'callback_data' => "recipe:view:{$r->id}"],
        ])->toArray();
        $buttons[] = [['text' => '« Categories', 'callback_data' => 'recipe:categories']];

        Telegram::editMessageText([
            'chat_id'      => $chatId,
            'message_id'   => $msgId,
            'text'         => "*{$category?->name}*",
            'parse_mode'   => 'Markdown',
            'reply_markup' => json_encode(['inline_keyboard' => $buttons]),
        ]);
    }

    public function handleView(Update $update, int $recipeId): void
    {
        $cbq    = $update->getCallbackQuery();
        $chatId = $cbq->getMessage()->getChat()->getId();
        $msgId  = $cbq->getMessage()->getMessageId();

        Telegram::answerCallbackQuery(['callback_query_id' => $cbq->getId()]);

        $recipe = Recipe::with('category')->find($recipeId);

        if (!$recipe) {
            Telegram::editMessageText([
                'chat_id'    => $chatId,
                'message_id' => $msgId,
                'text'       => 'Recipe not found.',
                'reply_markup' => json_encode(Keyboards::backButton('recipe:categories', '« Categories')),
            ]);
            return;
        }

        $content = mb_strlen($recipe->content) > 4000
            ? mb_substr($recipe->content, 0, 3997) . '...'
            : $recipe->content;

        $text = "*{$recipe->name}*\n_{$recipe->category?->name}_\n\n{$content}";

        Telegram::editMessageText([
            'chat_id'      => $chatId,
            'message_id'   => $msgId,
            'text'         => $text,
            'parse_mode'   => 'Markdown',
            'reply_markup' => json_encode(Keyboards::backButton("recipe:list:{$recipe->category_id}", '« Back')),
        ]);
    }
}
