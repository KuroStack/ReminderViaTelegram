<?php

namespace App\Telegram\Handlers\Admin;

use App\Models\Recipe;
use App\Models\RecipeCategory;
use App\Telegram\ConversationManager;
use App\Telegram\Guards;
use App\Telegram\Keyboards;
use Telegram\Bot\Laravel\Facades\Telegram;
use Telegram\Bot\Objects\Update;

class RecipeAdminHandler
{
    public function __construct(private ConversationManager $conv) {}

    public function handleAddStart(Update $update): void
    {
        $cbq    = $update->getCallbackQuery();
        $userId = $cbq->getFrom()->getId();

        if (!Guards::requireAdmin($userId, $cbq->getId())) {
            return;
        }

        Telegram::answerCallbackQuery(['callback_query_id' => $cbq->getId()]);

        $categories = RecipeCategory::all();

        if ($categories->isEmpty()) {
            Telegram::editMessageText([
                'chat_id'      => $cbq->getMessage()->getChat()->getId(),
                'message_id'   => $cbq->getMessage()->getMessageId(),
                'text'         => 'No recipe categories exist. Add one first.',
                'reply_markup' => json_encode(Keyboards::adminMenu()),
            ]);
            return;
        }

        $buttons = $categories->map(fn ($c) => [
            ['text' => $c->name, 'callback_data' => "admin:rec:cat:{$c->id}"],
        ])->toArray();
        $buttons[] = [['text' => '« Admin Menu', 'callback_data' => 'admin:menu']];

        $this->conv->setState($userId, 'arec:select_category');

        Telegram::editMessageText([
            'chat_id'      => $cbq->getMessage()->getChat()->getId(),
            'message_id'   => $cbq->getMessage()->getMessageId(),
            'text'         => 'Select a category for the new recipe:',
            'reply_markup' => json_encode(['inline_keyboard' => $buttons]),
        ]);
    }

    public function handleCatSelect(Update $update, int $catId): void
    {
        $cbq    = $update->getCallbackQuery();
        $userId = $cbq->getFrom()->getId();

        if (!Guards::requireAdmin($userId, $cbq->getId())) {
            return;
        }

        Telegram::answerCallbackQuery(['callback_query_id' => $cbq->getId()]);

        $category = RecipeCategory::find($catId);

        $this->conv->setState($userId, 'arec:enter_name', ['cat_id' => $catId, 'cat_name' => $category?->name]);

        Telegram::editMessageText([
            'chat_id'    => $cbq->getMessage()->getChat()->getId(),
            'message_id' => $cbq->getMessage()->getMessageId(),
            'text'       => "Category: *{$category?->name}*\n\nEnter the recipe name:",
            'parse_mode' => 'Markdown',
        ]);
    }

    public function handleName(Update $update): void
    {
        $msg    = $update->getMessage();
        $userId = $msg->getFrom()->getId();
        $chatId = $msg->getChat()->getId();

        $this->conv->mergePayload($userId, ['name' => trim($msg->getText())]);
        $this->conv->setState($userId, 'arec:enter_content', $this->conv->getPayload($userId));

        Telegram::sendMessage([
            'chat_id' => $chatId,
            'text'    => 'Enter the recipe content (ingredients, steps, etc.):',
        ]);
    }

    public function handleContent(Update $update): void
    {
        $msg    = $update->getMessage();
        $userId = $msg->getFrom()->getId();
        $chatId = $msg->getChat()->getId();

        $payload = $this->conv->getPayload($userId);

        Recipe::create([
            'category_id' => $payload['cat_id'],
            'name'        => $payload['name'],
            'content'     => trim($msg->getText()),
        ]);

        $this->conv->clearState($userId);

        Telegram::sendMessage([
            'chat_id'      => $chatId,
            'text'         => "Recipe *{$payload['name']}* saved.",
            'parse_mode'   => 'Markdown',
            'reply_markup' => json_encode(Keyboards::adminMenu()),
        ]);
    }
}
